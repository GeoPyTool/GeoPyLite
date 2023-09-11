import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

# 模拟参数
N = 100  # 网格数量
dt = 0.1  # 时间步长
F = 1000  # 外力
viscosity = 0.05  # 粘性

# 初始化变量
u = np.zeros((N, N))  # x速度
v = np.zeros((N, N))  # y速度
p = np.zeros((N, N))  # 压力

# 模拟一步
def simulate(u, v, p):
    u[50][50] += F * dt  # 在中心添加外力
    u[1:-1, 1:-1] += dt * (viscosity * (u[:-2, 1:-1] + u[2:, 1:-1] + u[1:-1, :-2] + u[1:-1, 2:] - 4*u[1:-1, 1:-1]) - (p[2:, 1:-1] - p[:-2, 1:-1]))
    v[1:-1, 1:-1] += dt * (viscosity * (v[:-2, 1:-1] + v[2:, 1:-1] + v[1:-1, :-2] + v[1:-1, 2:] - 4*v[1:-1, 1:-1]) - (p[2:, 2:] - p[:-2, :-2]))
    p[2:-2, 2:-2] += dt * ((u[3:-1, 2:-2] - u[1:-3, 2:-2]) + (v[2:-2, 3:-1] - v[2:-2, 1:-3]))

# 创建图形
fig = plt.figure()
ims = []

# 运行模拟并更新图形
for _ in range(10000):
    simulate(u, v, p)
    im = plt.imshow(np.sqrt(u**2+v**2), animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=200, blit=True,
                                repeat_delay=1000)

plt.show()
