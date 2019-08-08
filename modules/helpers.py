# useful for creating permutations with Ax. Sag. from Ax and Sag
def add_dot(s):
    ls = s.split(" ")
    ls[0] = ls[0] + "."
    ls = " ".join(ls)
    return ls


def create_perms(ls, addDot=False):
    if addDot:
        ls = [x.lower() for x in ls] + \
             [x.upper() for x in ls] + \
             [x.title() for x in ls] + \
             [add_dot(x).lower() for x in ls] + \
             [add_dot(x).upper() for x in ls] + \
             [add_dot(x).title() for x in ls]
    else:
        ls = [x.lower() for x in ls] + \
             [x.upper() for x in ls] + \
             [x.title() for x in ls]

    return ls


# define keyword dictionary for T1 and T2 sequences, which also encompasses T1CE and T2FLAIR.
kw = {
    't1': {
        'planes': ['ax', 'tra'],
        'neg': ['sag', 'cor', 'mprage'],
        'ops': ['pre', 'post', 'pg'],
        'contrast': ['gad', 'gd']
    },
    't2': {
        'planes': ['ax', 'tra'],
        'neg': ['sag', 'cor', 'mprage'],
        'ops': ['blade', 'flair'],
        'contrast': ['dark fluid', 'dark', 'fluid', 'fs', 'dark-fluid']
    }
}


def match_rule_t1(ser_desc, kw, reader=None, debug=False):
    seq = 't1'
    main_seq_key_name = ""
    # get plane permutations
    plane_perm = create_perms(kw[seq]['planes'], True)

    neg = create_perms(kw[seq]['neg'], True)

    # first find if there are any negative keywords present in this string
    for ne_kw in neg:
        if ne_kw in ser_desc:
            if debug:
                print('Found negative keyword {} in {}'.format(ne_kw, ser_desc))
            return {-1: 'invalid keyword'}

    # first find the plane
    f_plane = False
    for pl_kw in plane_perm:
        if f_plane == False and pl_kw in ser_desc:
            if debug:
                print('Found plane {} in {}'.format(pl_kw, ser_desc))
            f_plane = True
            break

    # get sequence permutations
    seq_perm = create_perms([seq])

    # find sequence
    f_seq = False
    for se_kw in seq_perm:
        if f_seq == False and se_kw in ser_desc:
            if debug:
                print('Found seq {} in {}'.format(se_kw, ser_desc))
            f_seq = True
            main_seq_key_name += "{}".format(se_kw.upper())
            break

    if not f_seq:
        return {-1: 'Cannot find sequence name, cannot assume sequence safely'}

    # find ops (pre, post, pg)

    ops_perm = create_perms(kw[seq]['ops'])

    f_op = False
    for op_kw in ops_perm:
        if f_op == False and op_kw in ser_desc:
            if debug:
                print('Found op {} in {}'.format(op_kw, ser_desc))
            f_op = op_kw.lower()
            if f_op == 'post' or f_op == 'pg' or f_op == False:
                # there's no pre or post, but there is GAD, assume its CE
                if reader is not None:
                    assert reader.GetMetaData(0,
                                              "0018|0010") != "", "Something is wrong, no contrast agent defined in DICOM!"
                main_seq_key_name += "CE"
            break

    # find contrast

    co_perm = create_perms(kw[seq]['contrast'])

    f_co = False
    for co_kw in co_perm:
        if co_kw in ser_desc:
            if debug:
                print('Found contrast {} in {}'.format(co_kw, ser_desc))
            if 'CE' not in main_seq_key_name and f_op != 'pre':
                main_seq_key_name += "CE"
            f_co = True
            break

    return main_seq_key_name


# %%
def match_rule_t2(ser_desc, kw, reader=None, debug=False):
    seq = 't2'
    main_seq_key_name = ""
    # get plane permutations
    plane_perm = create_perms(kw[seq]['planes'], True)

    neg = create_perms(kw[seq]['neg'], True)

    # first find if there are any negative keywords present in this string
    for ne_kw in neg:
        if ne_kw in ser_desc:
            if debug:
                print('Found negative keyword {} in {}'.format(ne_kw, ser_desc))
            return {-1: 'invalid keyword'}

    # first find the plane
    f_plane = False
    for pl_kw in plane_perm:
        if f_plane == False and pl_kw in ser_desc:
            if debug:
                print('Found plane {} in {}'.format(pl_kw, ser_desc))
            f_plane = True
            break

    # get sequence permutations
    seq_perm = create_perms([seq])

    # find sequence
    f_seq = False
    for se_kw in seq_perm:
        if f_seq == False and se_kw in ser_desc:
            if debug:
                print('Found seq {} in {}'.format(se_kw, ser_desc))
            f_seq = True
            main_seq_key_name += "{}".format(se_kw.upper())
            break

    if not f_seq:
        return {-1: 'Cannot find sequence name, cannot assume sequence safely'}

    # find ops (blade, flair)

    ops_perm = create_perms(kw[seq]['ops'])

    f_op = False
    for op_kw in ops_perm:
        if f_op == False and op_kw in ser_desc:
            if debug:
                print('Found op {} in {}'.format(op_kw, ser_desc))
            f_op = op_kw.lower()
            if f_op == 'flair':
                # there's no pre or post, but there is GAD, assume its CE
                main_seq_key_name += "FLAIR"
            break

    # find contrast

    co_perm = create_perms(kw[seq]['contrast'])

    f_co = False
    for co_kw in co_perm:
        if co_kw in ser_desc and not f_co:
            if debug:
                print('Found contrast {} in {}'.format(co_kw, ser_desc))
            if 'FLAIR' not in main_seq_key_name:
                main_seq_key_name += "FLAIR"
            f_co = True
            break

    return main_seq_key_name