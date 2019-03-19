import numpy as np
import linearmodels as lm

# https://bashtage.github.io/linearmodels/doc/index.html

# # # Example # # #

n_var = 1
n_ind = 222
t_max = 25

y = np.zeros((t_max, n_ind))

x = np.zeros((n_var, t_max, n_ind))

# Generate random data
x[:] = np.random.choice([0, 1], size=x.shape)
y[:] = np.random.random(y.shape)

# for t in range(t_max):
#  for i in range(n_ind):
#    # y[t, i] = i+np.random.random()
#    y[t, i] = np.random.random()
#    for v in range(n_var):
#      x[v, :, i] = i

print(x)
print(y)

a = lm.PanelOLS(
    dependent=y,
    exog=x,
    entity_effects=False,
    time_effects=False,
    other_effects=np.array(
        []
    )
)

print(a.fit(cov_type='clustered', cluster_entity=False))


# fit_bkup = load('fit.p')
# user_bkup = load('user.p')
#
# t_max = 12
# n_ind = 222
# n_var = 3
# heuristic = 'max_diff'
#
# # print([i[:t_max] for i in fit_bkup.t_fit_scores[heuristic]])
#
# y = np.zeros((t_max, n_ind))
#
# for i, y_i in enumerate(fit_bkup.t_fit_scores[heuristic]):
#     y[:, i] = y_i[:t_max]
#
# x = np.zeros((n_var, t_max, n_ind))
#
# nationalities = np.unique(user_bkup.nationality)
#
# for i, n in enumerate(nationalities):
#     user_bkup.nationality[user_bkup.nationality == n] = i
#
# user_bkup.gender[user_bkup.gender == "male"] = 0
# user_bkup.gender[user_bkup.gender == "female"] = 1
#
# for i in range(n_ind):
#     x[0, :, i] = user_bkup.gender[i]  # np.random.choice([0, 1])
#     x[1, :, i] = user_bkup.age[i]  # np.random.random()
#     x[2, :, i] = user_bkup.nationality[i]  # np.random.random()
#     # x[3, :, i] = np.arange''

# # n_var = 1
# # n_ind = 222
# # t_max = 25
#
# # y = np.zeros((t_max, n_ind))
# #
# # x = np.zeros((n_var, t_max, n_ind))
#
# # Generate random data
# # x[:] = np.random.random(x.shape)
# # y[:] = np.random.random(y.shape)
#
# # for t in range(t_max):
# #  for i in range(n_ind):
# #    # y[t, i] = i+np.random.random()
# #    y[t, i] = np.random.random()
# #    for v in range(n_var):
# #      x[v, :, i] = i
#
# # print(x)
# # print(y)
#
# a = lm.PanelOLS(
#     dependent=y,
#     exog=x,
#     entity_effects=False,
#     time_effects=True
# )
#
# print(a.fit())  # cov_type='clustered', cluster_entity=True))
