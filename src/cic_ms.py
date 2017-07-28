import numpy as np
import math
import bct


# returns value of st.dev w_alpha_beta across all choose 2 in cmt_str_lst_lst
def calc_std_w_alpha_beta(roi_name_lst, cmt_str_lst_lst, res_dct):
    w_a_b_vals = np.array([])  # maintain list for all values
    num_vals = n_choose_2(len(cmt_str_lst_lst))
    w_a_b_vals.resize(num_vals)
    w_a_b_index = 0
    for alpha_index, alpha in enumerate(cmt_str_lst_lst):
        alpha_fs_lst = [frozenset(cmt) for cmt in alpha]
        for beta in cmt_str_lst_lst[alpha_index + 1:]:
            beta_fs_lst = [frozenset(cmt) for cmt in beta]
            w_a_b_vals[w_a_b_index] = \
                w_alpha_beta(
                    roi_name_lst,
                    alpha_fs_lst,
                    beta_fs_lst,
                    res_dct)['alpha_and_beta']
            w_a_b_index += 1
    return np.std(w_a_b_vals)


# returns dict of alpha_only, beta_only and alpha_and_beta results:
#  ('alpha_only' : ..., 'beta_only' : ..., 'alpha_and_beta' : ...)
# input
#  res_dct: frozenset dict of previous results { fs(fs(alpha), fs(beta)): ...}
def w_alpha_beta(roi_name_lst, alpha_fs_lst, beta_fs_lst, res_dct):
    # count up all the shaired pairs between alpha and beta
    key = frozenset([frozenset(alpha_fs_lst), frozenset(beta_fs_lst)])
    ret_val = {'alpha_only': 0, 'beta_only': 0, 'alpha_and_beta': 0}

    if(key not in res_dct):
        for a_index, roi_name_a in enumerate(roi_name_lst):
            for roi_name_b in roi_name_lst[a_index + 1:]:
                piab = pair_in_alpha_beta(roi_name_a, roi_name_b,
                                          alpha_fs_lst,
                                          beta_fs_lst)

                ret_val['alpha_only'] += piab['alpha_only']
                ret_val['beta_only'] += piab['beta_only']
                ret_val['alpha_and_beta'] += piab['alpha_and_beta']
        res_dct[key] = ret_val  # store results for subsequent call

    return res_dct[key]


# returns a tuple:
#  (mean_z_score_rand_coef, var_z_score_rand_coef)
def calc_mean_var_z_alpha_beta(roi_name_lst, std_w_alpha_beta, cmt_str_lst_lst,
                               M, res_dct):
    z_alpha_beta_vals = np.array([])
    num_vals = n_choose_2(len(cmt_str_lst_lst))
    z_alpha_beta_vals.resize(num_vals)
    z_alpha_beta_index = 0
    # compare all community structures once and record z alpha beta vals
    for alpha_index, alpha in enumerate(cmt_str_lst_lst):
        for beta in cmt_str_lst_lst[alpha_index + 1:]:
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
                     alpha_fs_lst=[frozenset(cmt) for cmt in alpha],
                     beta_fs_lst=[frozenset(cmt) for cmt in beta],
                     res_dct=res_dct)
    return (1/std_w_alpha_beta) * d['alpha_and_beta'] -\
        (d['alpha_only'] * d['beta_only'])/float(M)


# returns
#  tripple of (alpha_only, beta_only, alpha_and_beta)
#   True if roi_name_a and roi_name_b in community in both alpha and beta
#   False otherwise
def pair_in_alpha_beta(roi_name_a, roi_name_b, alpha, beta):
    in_alpha = False
    for cmt in alpha:
        if roi_name_a in cmt and roi_name_b in cmt:
            in_alpha = True

    in_beta = False
    for cmt in beta:
        if roi_name_a in cmt and roi_name_b in cmt:
            in_beta = True

    return {'alpha_only': alpha_only(in_alpha, in_beta),
            'beta_only': beta_only(in_alpha, in_beta),
            'alpha_and_beta': alpha_and_beta(in_alpha, in_beta)}


def calc_cons_cmt_str(roi_name_lst, cmt_str_lst_lst, gamma, runs, tau):
    D = cons_mtx_npa(roi_name_lst=roi_name_lst,
                     cmt_str_lst_lst=cmt_str_lst_lst)
    D[D < tau] = 0
    non_zero_D = np.extract(D != 0, D)
    while(len(np.extract(non_zero_D != 1, non_zero_D)) > 1):
        cmt_str_lst_lst = run_louvain(roi_name_lst=roi_name_lst,
                                      ctx_mtx_npa=D,
                                      gamma=gamma,
                                      runs=runs)
        D = cons_mtx_npa(roi_name_lst=roi_name_lst,
                         cmt_str_lst_lst=cmt_str_lst_lst)
        D[D < tau] = 0
        non_zero_D = np.extract(D != 0, D)
    return cmt_str(roi_name_lst, D)


# returns
#  consensus matrix D, Dij=num of partitions that i, j share cmt/len partitions
def cons_mtx_npa(roi_name_lst, cmt_str_lst_lst):
    ret_val = np.zeros((len(roi_name_lst), len(roi_name_lst)))
    # make consensus matrix for each row_roi to col_roi
    for row_idx, row_roi in enumerate(roi_name_lst):
        for col_idx, col_roi in enumerate(roi_name_lst):
            if row_idx != col_idx:
                num_shared = 0
                for cmt_lst in cmt_str_lst_lst:
                    for cmt in cmt_lst:
                        if row_roi in cmt and col_roi in cmt:
                            num_shared += 1
                ret_val[row_idx, col_idx] = num_shared

    num_parts = float(len(cmt_str_lst_lst))
    ret_val /= num_parts
    return ret_val


# returns community structure list [ [roi_name1, roi_name2,...], ... [...] ]
#  from consensus matrix
def cmt_str(roi_name_lst, cons_mtx_npa):
    cmt_str_lst = []
    for row_idx, row_roi in enumerate(roi_name_lst):
        for col_idx, col_roi in enumerate(roi_name_lst):
            # always add roi if not there so it at least belongs to its own cmt

            if row_idx == col_idx:
                if len([cmt for cmt in cmt_str_lst if row_roi in cmt]) == 0:
                    cmt_str_lst.append([row_roi])
            elif cons_mtx_npa[row_idx, col_idx] > 0:
                cur_lst = [cmt
                           for cmt in cmt_str_lst
                           if row_roi in cmt or col_roi in cmt]
                # will convert everything to single values at the end
                assert(len(cur_lst)) <= 1
                if len(cur_lst) == 0:
                    cmt_str_lst.append([row_roi, col_roi])
                else:
                    new = cur_lst[0] + [row_roi, col_roi]
                    cmt_str_lst[cmt_str_lst.index(cur_lst[0])] = new
    return sorted([sorted(frozenset(cmt)) for cmt in cmt_str_lst])


# returns cmt_str_lst_lst from louvain
def run_louvain(roi_name_lst, ctx_mtx_npa, gamma, runs):
    cmt_str_lst_lst = []
    for run_index in xrange(runs):
        (ci, q) = bct.modularity_louvain_dir(W=ctx_mtx_npa, gamma=gamma)

        assert len(ci) == len(roi_name_lst),\
            "Uh-oh, found commmunities don't make sense"

        cmt_str_dct = {}
        for roi_idx, roi in enumerate(roi_name_lst):
            cmt_lst = cmt_str_dct.get(ci[roi_idx], [])
            cmt_lst.append(roi)
            cmt_str_dct[ci[roi_idx]] = sorted(cmt_lst)

        cmt_str_lst_lst.append(sorted([cmt_str_dct[cmt_str_key]
                                       for cmt_str_key in cmt_str_dct.keys()]))

    return cmt_str_lst_lst


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
