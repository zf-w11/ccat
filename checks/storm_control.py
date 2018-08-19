# Storm-control options check
# Input:
#        interface dictionary
#        config result dictionary
# Output:
#        updated result dictionary
#           {{'iface1': {'Storm-control': {'storm level': [severity(int), 'message', 'best practice'],'multicast storm':...}, 'iface2':...}}
#

# check storm-control level
# if level incorrect return [0,level, maximum appropriate level]
# import re

from re import findall

def storm_lvl_check(lvl,storm_level,scale):
    # return ([1,80] if float(lvl) < 80.0 else [0,lvl,80])
    if float(lvl) < storm_level:
        return [scale[2], lvl]
    else:
        return [scale[0], lvl, 'Storm-control level should be less than 80']


# check storm-control traffic type
def check_storm_type(type_storm, result, flag,scale):
    type_dct = {'broadcast': 0, 'multicast': 0, 'unicast': 0}
    if flag:
        for each in type_storm:
            type_dct = iter_type(each, type_dct)
    else:
        type_dct = iter_type(type_storm, type_dct)
    for each in type_dct:
        if type_dct[each] == 1:
            result.update({each.capitalize()+' traffic Storm Control': [scale[2], 'ENABLED']})

    return result


def iter_type(each, type_dct):
    if each in type_dct:
        type_dct[each] = 1
    return type_dct


def _storm_check(iface_dct,storm_level,scale,dct):

    # dct = {}
    if 'storm control' in iface_dct and len(iface_dct['storm control']) != 0:
        storm_dct = iface_dct['storm control']
        # check storm-control level

        if 'level' in storm_dct:
            for i in range(len(storm_dct['level'])):
                lvl_type = storm_dct['level'][i][0]
                lvl_list = storm_dct['level'][i][1]


                lvl_list = findall(r'([\d\.]+)', lvl_list)
                # if level pps[bps] level_1 level_2
                if len(lvl_list) == 2:
                    if lvl_list[0] > lvl_list[1] or lvl_list[0] != lvl_list[1]:
                        if float(lvl_list[0]) == 0 or float(lvl_list[1]) == 0 or float(
                                lvl_list[0]) == 100 or float(lvl_list[1]) == 100 or float(
                            lvl_list[0]) == 1 or float(lvl_list[1]) == 1:
                            dct.update(
                                {'The traffic Storm Control level': [scale[0], 'INCORRECT', 'Storm Control level should be less than 80(0.8)']})
                        else:
                            dct.update({'The traffic Storm Control level': storm_lvl_check(lvl_list[0],storm_level,scale)})
                    else:
                        dct.update({'The traffic Storm Control level': [scale[0], 'INCORRECT', 'Storm Control level shouldn`t be equal']})
                else:
                    if float(lvl_list[0]) == 0 or float(lvl_list[0]) == 100 or float(lvl_list[0]) == 1:
                        dct.update({'The traffic Storm Control level': [scale[0], 'INCORRECT', 'Storm Control level shouldn`t be equal 1(100) or 0']})
                    else:
                        dct.update({'The traffic Storm Control level': storm_lvl_check(lvl_list[0],storm_level,scale)})

                # check storm-control traffic type

                check_storm_type(lvl_type, dct, 0,scale)
        else:
            dct.update(
                {'The traffic Storm Control level': [scale[0], 'DISABLED', 'Storm-control level should be turn on']})

        if 'type' in storm_dct:
            dct.update(check_storm_type(storm_dct['type'], dct, 1,scale))

        for each in ['broadcast', 'multicast', 'unicast']:
            if each not in dct:
                if each == 'unicast':
                    dct.update({each.capitalize()+' traffic Storm Control': [scale[1], 'DISABLED', each.capitalize() + ' Storm Control should be turn on']})
                else:
                    dct.update({each.capitalize()+' traffic Storm Control': [scale[0], 'DISABLED', each.capitalize() + ' Storm Control should be turn on']})
    else:
        dct.update({'Traffic Storm Control': [scale[0], 'DISABLED', 'Storm Control should be enable']})
        return dct

    return dct

def check(iface_dct, vlanmap_type,storm_level=80):
    result = {}
    print(vlanmap_type)
# If this network segment is TRUSTED - enabled cdp is not a red type of threat, it will be colored in orange
    if vlanmap_type == 'TRUSTED':
        _storm_check(iface_dct,storm_level,[1,1,2],result)

# Otherwise if network segment is CRITICAL or UNKNOWN or vlanmap is not defined - enabled cdp is a red type of threat
    else:
        _storm_check(iface_dct, storm_level, [0,1, 2], result)


    return result

