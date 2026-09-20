import matplotlib.pylab as plt
import pandas as pd
import numpy as np


esc_max_pid_throttle = 960000
esc_min_pid_throttle = 0


fig = plt.figure()
fig.subplots_adjust(hspace=0.4, wspace=0.4)

fig.set_size_inches(20, 30, forward=True)

df = pd.read_csv('data.csv')

df = df.set_index('total_time')

ax = fig.add_subplot(3, 1, 1)  ##########
#
t_min = min(df.index.values)
t_max = max(df.index.values)




ax.plot(df.index.values, df['roll_angle'].values, label='roll_angle')
# ax.plot(df.index.values, df['pitch_angle'].values, label='pitch_angle')



plt.grid()
plt.legend()



ax = fig.add_subplot(3, 1, 2)  ##########




ax.plot(df.index.values, df['esc_1_v'].values, label='esc_1_v', c='red', lw=1)
ax.plot(df.index.values, df['esc_4_v'].values, label='esc_4_v', c='blue', lw=1)

ax.plot(df.index.values, df['esc_2_v'].values, label='esc_2_v', c='green', lw=1)
ax.plot(df.index.values, df['esc_3_v'].values, label='esc_3_v', c='brown', lw=1)

ax.plot([t_min, t_max], [esc_max_pid_throttle, esc_max_pid_throttle], label='esc_max_pid_throttle', c='red', lw=0.3)
ax.plot([t_min, t_max], [esc_min_pid_throttle, esc_min_pid_throttle], label='esc_min_pid_throttle', c='red', lw=0.3)




plt.grid()
plt.legend()



ax = fig.add_subplot(3, 1, 3)  ##########

t_min = min(df.index.values)
t_max = max(df.index.values)


ax.plot(df.index.values, df['pid_roll'].values, label='pid_roll', c='red', lw=1)
ax.plot(df.index.values, df['pid_roll.p'].values, label='pid_roll.p', c='blue', lw=1)
ax.plot(df.index.values, df['pid_roll.i'].values, label='pid_roll.i', c='green', lw=1)
ax.plot(df.index.values, df['pid_roll.d'].values, label='pid_roll.d', c='brown', lw=1)





plt.grid()
plt.legend()


plt.show()

sd=3
