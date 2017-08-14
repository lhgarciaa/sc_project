import numpy as np
import math
import bct


# returns value of st.dev w_alpha_beta across all choose 2 in cmt_str_lst_lst
# only accept a frozenset of frozensets to speed things up
def calc_std_w_alpha_beta(roi_name_lst, cmt_str_lst_fs_fs, res_dct):
    # make sure we're working with frozensets for performance reasons
    assert(len(cmt_str_lst_fs_fs) > 0)  # reasonable assumption
    assert type(cmt_str_lst_fs_fs[0]) == frozenset, \
        "Convert type {} of {} to frozensets".format(
            type(cmt_str_lst_fs_fs[0]),
            cmt_str_lst_fs_fs[0])
    assert(len(cmt_str_lst_fs_fs[0]) > 0)
    assert type(next(iter(cmt_str_lst_fs_fs[0]))) == frozenset, \
        "Convert type {} of {} to frozensets".format(
            type(next(iter(cmt_str_lst_fs_fs[0]))),
            next(iter(cmt_str_lst_fs_fs[0])))

    w_a_b_vals = np.array([])  # maintain list for all values
    num_vals = n_choose_2(len(cmt_str_lst_fs_fs))
    w_a_b_vals.resize(num_vals)
    w_a_b_index = 0
    for alpha_index, alpha in enumerate(cmt_str_lst_fs_fs):
        for beta in cmt_str_lst_fs_fs[alpha_index + 1:]:
            w_a_b_vals[w_a_b_index] = \
                w_alpha_beta(
                    roi_name_lst,
                    alpha,
                    beta,
                    res_dct)['alpha_and_beta']
            w_a_b_index += 1
    return np.std(w_a_b_vals)


# returns a tuple:
#  (mean_z_score_rand_coef, var_z_score_rand_coef)
# returns (inf, nan) if std_w_alpha_beta is 0
def calc_mean_var_z_alpha_beta(roi_name_lst, std_w_alpha_beta,
                               cmt_str_lst_fs_fs,
                               M, res_dct):
    # make sure we're working with frozensets for performance reasons
    assert(len(cmt_str_lst_fs_fs) > 0)  # reasonable assumption
    assert type(cmt_str_lst_fs_fs[0]) == frozenset, \
        "Convert type {} of {} to frozensets".format(
            type(cmt_str_lst_fs_fs[0]),
            cmt_str_lst_fs_fs[0])
    assert(len(cmt_str_lst_fs_fs[0]) > 0)
    assert type(next(iter(cmt_str_lst_fs_fs[0]))) == frozenset, \
        "Convert type {} of {} to frozensets".format(
            type(next(iter(cmt_str_lst_fs_fs[0]))),
            next(iter(cmt_str_lst_fs_fs[0])))

    if std_w_alpha_beta == 0:
        return (float('Inf'), float('NaN'))
    z_alpha_beta_vals = np.array([])
    num_vals = n_choose_2(len(cmt_str_lst_fs_fs))
    z_alpha_beta_vals.resize(num_vals)
    z_alpha_beta_index = 0
    # compare all community structures once and record z alpha beta vals
    for alpha_index, alpha in enumerate(cmt_str_lst_fs_fs):
        for beta in cmt_str_lst_fs_fs[alpha_index + 1:]:
            z_alpha_beta_vals[z_alpha_beta_index] = \
                calc_z_alpha_beta(roi_name_lst=roi_name_lst,
                                  std_w_alpha_beta=std_w_alpha_beta,
                                  alpha=alpha,
                                  beta=beta,
                                  M=M,
                                  res_dct=res_dct)
            z_alpha_beta_index += 1
    return (np.mean(z_alpha_beta_vals), np.var(z_alpha_beta_vals))


# returns a single value:
#  z_score_rand_coef
def calc_z_alpha_beta(roi_name_lst, std_w_alpha_beta, alpha, beta, M, res_dct):
    # return (1/std w_alpha_beta) * w_alpha_beta - (Ma*Mb)/M
    d = w_alpha_beta(roi_name_lst=roi_name_lst,
                     alpha=alpha,
                     beta=beta,
                     res_dct=res_dct)
    return (1/std_w_alpha_beta) * d['alpha_and_beta'] -\
        (d['alpha_only'] * d['beta_only'])/float(M)


# returns dict of alpha_only, beta_only and alpha_and_beta results:
#  ('alpha_only' : ..., 'beta_only' : ..., 'alpha_and_beta' : ...)
# input
#  res_dct: frozenset dict of previous results { fs(fs(alpha), fs(beta)): ...}
def w_alpha_beta(roi_name_lst, alpha, beta, res_dct):
    # count up all the shaired pairs between alpha and beta
    key = frozenset({alpha, beta})
    ret_val = {'alpha_only': 0, 'beta_only': 0, 'alpha_and_beta': 0}

    if(key not in res_dct):
        for a_index, roi_name_a in enumerate(roi_name_lst):
            for roi_name_b in roi_name_lst[a_index + 1:]:
                piab = pair_in_alpha_beta(roi_name_a,
                                          roi_name_b,
                                          alpha,
                                          beta)

                ret_val['alpha_only'] += piab['alpha_only']
                ret_val['beta_only'] += piab['beta_only']
                ret_val['alpha_and_beta'] += piab['alpha_and_beta']
        res_dct[key] = ret_val  # store results for subsequent call

    return res_dct[key]


# input
#  roi_name_a, roi_name_b
#  alpha: fs_fs community structure e.g. frozenset(frozenset('A', 'B'),
#                                                  frozenset('C'))
#  beta:  fs_fs community structure
# returns
#  triple of (alpha_only, beta_only, alpha_and_beta)
#   True if roi_name_a and roi_name_b in community in both alpha and beta
#   False otherwise
def pair_in_alpha_beta(roi_name_a, roi_name_b, alpha, beta):
    in_alpha = pair_in_fs_fs(roi_name_a=roi_name_a,
                             roi_name_b=roi_name_b,
                             fs_fs=alpha)

    in_beta = pair_in_fs_fs(roi_name_a=roi_name_a,
                            roi_name_b=roi_name_b,
                            fs_fs=beta)

    return {'alpha_only': alpha_only(in_alpha, in_beta),
            'beta_only': beta_only(in_alpha, in_beta),
            'alpha_and_beta': alpha_and_beta(in_alpha, in_beta)}


def calc_cons_cmt_str(roi_name_lst, cmt_str_lst_fs_fs, gamma, runs, tau):
    D = cons_mtx_npa(roi_name_lst=roi_name_lst,
                     cmt_str_lst_fs_fs=cmt_str_lst_fs_fs)
    D[D < tau] = 0
    non_zero_D = np.extract(D != 0, D)
    while(len(np.extract(non_zero_D != 1, non_zero_D)) > 1):
        cmt_str_lst_fs_fs = run_louvain(roi_name_lst=roi_name_lst,
                                        ctx_mtx_npa=D,
                                        gamma=gamma,
                                        runs=runs)
        D = cons_mtx_npa(roi_name_lst=roi_name_lst,
                         cmt_str_lst_fs_fs=cmt_str_lst_fs_fs)
        D[D < tau] = 0
        non_zero_D = np.extract(D != 0, D)
    return cmt_str(roi_name_lst, D)


# speediest check of roi_name_a and roi_name_b being in same fs in fs_fs
def pair_in_fs_fs(roi_name_a, roi_name_b, fs_fs):
    for fs in fs_fs:
        roi_name_a_in = roi_name_a in fs
        roi_name_b_in = roi_name_b in fs

        if roi_name_a_in and not roi_name_b_in:
            return(False)
        elif not roi_name_a_in and roi_name_b_in:
            return(False)
        elif roi_name_a_in and roi_name_b_in:
            return(True)
    return False


# returns
#  consensus matrix D, Dij=num of partitions that i, j share cmt/len partitions
def cons_mtx_npa(roi_name_lst, cmt_str_lst_fs_fs):
    ret_val = np.zeros((len(roi_name_lst), len(roi_name_lst)))
    # make consensus matrix for each row_roi to col_roi

    for row_idx, row_roi in enumerate(roi_name_lst):
        for col_idx, col_roi in enumerate(roi_name_lst):
            if row_idx != col_idx:
                num_shared = 0
                for cmt_str_fs_fs in cmt_str_lst_fs_fs:
                    # similar logic as pair_in_alpha_beta for speedup
                    if(pair_in_fs_fs(roi_name_a=row_roi,
                                     roi_name_b=col_roi,
                                     fs_fs=cmt_str_fs_fs)):
                        num_shared += 1
                ret_val[row_idx, col_idx] = num_shared

    num_parts = float(len(cmt_str_lst_fs_fs))
    ret_val /= num_parts
    return ret_val


# returns community structure list [ [roi_name1, roi_name2,...], ... [...] ]
#  from consensus matrix
def cmt_str(roi_name_lst, cons_mtx_npa):
    # first create a dct of {roi_idx: frozenset({roi_idx}) use
    #  idx instead of actual name to save space
    cmt_str_dct = {}
    for roi_idx in xrange(len(roi_name_lst)):
        cmt_str_dct[roi_idx] = frozenset({roi_idx})

    # now for each row_roi and col_roi
    #  if row_roi and col_roi share a cmt
    #   create union of cmt_str_dct[row_roi] w/ cmt_str_dct[col_roi]
    #   assign union to every roi w/in union
    for row_idx in xrange(len(roi_name_lst)):
        for col_idx in xrange(len(roi_name_lst)):
            if cons_mtx_npa[row_idx, col_idx] > 0:
                union_set = cmt_str_dct[row_idx].union(cmt_str_dct[col_idx])
                for roi_idx in union_set:
                    cmt_str_dct[roi_idx] = union_set

    # frozenset of values will contain just the sets of roi_idx with no dups
    #  format community structure list and return that
    cmt_str_dct_vals_fs = frozenset(cmt_str_dct.values())

    cmt_str_lst = []
    # convert to roi names
    for roi_idx_fs in cmt_str_dct_vals_fs:
        cmt_str = []
        for roi_idx in roi_idx_fs:
            cmt_str.append(roi_name_lst[roi_idx])
        cmt_str_lst.append(sorted(cmt_str))

    return sorted(cmt_str_lst)


# returns cmt_str_lst_fs_fs from louvain
def run_louvain(roi_name_lst, ctx_mtx_npa, gamma, runs):
    cmt_str_lst_fs_fs = []
    for run_index in xrange(runs):
        (ci, q) = bct.modularity_louvain_dir(W=ctx_mtx_npa, gamma=gamma)

        assert len(ci) == len(roi_name_lst),\
            "Uh-oh, found commmunities don't make sense"

        cmt_str_dct = {}
        for roi_idx, roi in enumerate(roi_name_lst):
            cmt_fs = cmt_str_dct.get(ci[roi_idx], frozenset())
            cmt_fs = cmt_fs.union({roi})
            cmt_str_dct[ci[roi_idx]] = cmt_fs

        cmt_str_lst_fs_fs.append(frozenset([cmt_str_dct[cmt_str_key]
                                            for cmt_str_key in
                                            cmt_str_dct.keys()]))

    return cmt_str_lst_fs_fs


def alpha_only(in_alpha, in_beta):
    return in_alpha and not in_beta


def beta_only(in_alpha, in_beta):
    return not in_alpha and in_beta


def alpha_and_beta(in_alpha, in_beta):
    return in_alpha and in_beta


# finds number of pairs
def n_choose_2(num_rois):
    return(math.factorial(num_rois) /
           (math.factorial(2) * math.factorial(num_rois - 2)))


def fs_fs_to_lst_lst(fs_fs):
    lst_lst = []
    for fs in fs_fs:
        lst_lst.append(list(fs))
    return lst_lst


def lst_fs_fs_to_lst_lst_lst(lst_fs_fs):
    lst_lst_lst = []
    for fs_fs in lst_fs_fs:
        lst_lst = fs_fs_to_lst_lst(fs_fs)
        lst_lst_lst.append(sorted(lst_lst))
    return sorted(lst_lst_lst)


def lst_lst_to_fs_fs(lst_lst):
    return frozenset([frozenset(lst) for lst in lst_lst])
