---
title: "推导 Baxter and King (1993) 中 Equation (14)-(18)"
date: 2025-12-27T14:55:35-06:00
draft: false
summary: "在 GPT 老师的帮助下好不容易推明白了，要在一不小心把草纸扔了之前给记下来！"
categories: ["一步踏错终身错"]
tags: ["Macro"]
---

{{< katex >}}

这篇论文扩展了 neoclassical model，在其中加入了公共资本和公共投资，用来研究政府购买和投资对于经济增长的影响。模型中，政府可以通过 lump-sum tax 或者比例税收来资助政府购买与公共投资，政府也可以选择暂时增加支出（比如战争）或者永久增加支出。这篇论文非常重要的一个贡献在于将公共资本融入了生产函数，而量化模拟结果对公共资本的规模报酬变化十分敏感。本文中推导的 Eq (14)-(18) 主要集中关注政府购买的情况，因此公共资本在生产函数中没有出现。

## Setup

- Representative agents.
- Infinite horizon.

### Preference

\\[U(\cdot) = \mathbb{E}\_1\sum\_{t=1}^\infty \beta^{(t-1)}\left[\log (C_t) + \theta_L \log (L_t) + \Gamma(G_t^B, K_t^G)\right]\\]

- \\(C_t\\): 消费
- \\(L_t\\): leisure
- \\(G_t^B\\): 政府购买
- \\(K_t^G\\): 公共资本

### Technology

$$Y_t = F(K_t, K_t^G, N_t) = AK_t^{\theta_K}N_t^{\theta_N}\textcolor{blue}{(K_t^G)^{\theta_G}}$$

- \\(K_t\\): 私人资本
- \\(\textcolor{blue}{K_t^G}\\): 公共资本
- \\(N_t\\): 劳动投入
- 私人投入 Constant returns to scale: \\(\theta_K + \theta_N = 1\\)

### Capital Evolution

- \\( K\_{t+1} = \left[(1-\delta_K)K_t + I_t\right] \\)
- \\( \textcolor{blue}{K\_{t+1}^G} \textcolor{blue}{= \left[(1-\delta_K)K_t^G + I_t^G\right]}\\)

### Resource Constraints

- Household:
  - \\(L_t + N_t \leq 1\\)
  - \\(C_t + I_t \leq (1-\tau_t)Y_t + \text{TR}\_t\\)
- Economy: \\(C_t + I_t + G_t \leq Y_t\\), where \\(G_t := G_t^B + I_t^G\\)

### Public Finance Rules

\\[\tau_t Y_t = G_t + \text{TR}_t\\]

- Lump-sum tax: \\(\tau_t = 0\\), 使用 \\(\text{TR}\_t\\) 资助政府购买
- 比例税率:
  - \\(\tau_t = \frac{G_t + \text{TR}\_t}{Y_t}\\)
  - 假设转移支付恒定：\\(\Delta \text{TR} = 0\\)

### Characterizing the Equilibrium

用 Lagrangian 和 First order conditions 很容易可以写出以下三个式子

- \\(\frac{\partial U(C_t, L_t, G_t^B, K_t^G)}{\partial C_t} = \lambda_t\\)
- \\(\frac{\partial U(C_t, L_t, G_t^B, K_t^G)}{\partial L_t} = \lambda_t w_t,\\) where \\(\textcolor{blue}{w_t = (1-\tau_t)\frac{\partial F(\cdot)}{\partial N_t}}\\)
- \\(\beta\mathbb{E}\_t\bigl[\lambda\_{t+1}\bigl(1+q\_{t+1}-\delta_K \bigr)\bigr] = \lambda_t,\\) where \\( \textcolor{blue}{q_t = (1-\tau_t)\frac{\partial F(\cdot)}{\partial K_t}}\\)

以及 transversality condition

- \\(\mathbb{E}\_1\left[\lim\_{t\rightarrow\infty} \beta^t\lambda_t K\_{t+1}\right] = 0\\)

为了简化式子，文章中定义了以下几个符号：

- 资本劳动比 \\(\kappa = K/N\\)
- Average product of labor \\(\alpha = Y/N\\)
- 资本收入占国民收入比例 \\(s_K = qK/Y = q\kappa/\alpha \\)
- 投资占国民收入比例 \\(s_I = I/Y\\)
- 劳动收入占国民收入比例 \\(s_N = wN/Y = w/\alpha\\)
- Share of leisure in full income: \\(s_L^f = wL/Y^f\\)
- Full-income elasticity of leisure \\(\eta_L = \frac{\Delta L/L}{\Delta Y^f/Y^f}\\)

## Equation (14), (15)

Eq (14): \\(C_t +wL \leq Y^f\\)

Eq (15): \\(\frac{\Delta Y}{\Delta G} = = s_L^f\eta_L\\)

这一部分考虑静态模型，假设用 lump-sum tax 来资助政府购买支出，即\\(\tau_t = 0\\)。假设 w 不变，我们可以定义 full income \\(Y^f\\)为一个人可以得到的收入上限\\(Y^f := w + \Pi\\)，而在 lump-sum tax 的情况下，\\(\Pi = -G\\)。由于\\(C_t \leq w(1-L)+ \Pi\\)，经过简单的替换，我们可以得到 Eq (14) \\(C_t +wL \leq Y^f\\)。

\\(Y^f = w - G \Rightarrow \Delta Y^f = -\Delta G\\)

\\(N := 1-L \Rightarrow \Delta N = -\Delta L\\)

\\[\begin{aligned}
\frac{\Delta Y}{\Delta G} = \frac{\Delta Y}{\Delta N}\frac{\Delta N}{\Delta Y^f}\frac{\Delta Y^f}{\Delta G} = w\frac{-\Delta L}{\Delta Y^f}(-1)= w\frac{L}{Y^f}\frac{Y^f}{L}\frac{\Delta L}{\Delta Y^f} = s_L^f\eta_L
\end{aligned}\\]

由此，我们也得到文章中的 Eq (15)。

## Equation (16)

Eq (16): \\(\frac{\Delta Y}{\Delta G} = \frac{s_L^f \eta_L/s_N }{1+s_L^f \eta_L(s_K - s_I)/s_N }\\)

这一部分考虑动态模型，因此我们考虑 Capital law of motion。在这种情况下，收入上限中除了劳动收入，还包括资本收入、投资支出和政府支出。因此\\(Y^f = w +qK - I- G\\)。如果我们集中关注稳态中的投资支出，那么我么可以得到\\( K = (1-\delta_K)K + I \\)，即\\( I= \delta_K K \\)。

我们也可以使用\\(\kappa, \alpha, \delta_K\\)来表示\\(s_I\\)

\\[s_I = \frac{I}{Y} = \frac{I}{K}\frac{K}{N}\frac{N}{Y} = \delta_K \frac{\kappa}{\alpha}\\]

因此,

\\[\begin{aligned}
Y^f &= w +qK - I- G = w +qK - \delta_K K- G = w +(q - \delta_K) K- G \\\
 &= w +(q - \delta_K) \kappa N \frac{\alpha}{\alpha} - G = w +\alpha(\frac{\kappa q}{\alpha} - \frac{\delta_K \kappa}{\alpha}) N - G\\\
 &= w +\alpha(s_K - s_I) N - G
\end{aligned}\\]

由全微分得到 \\(\Delta Y^f= \alpha(s_K - s_I) \Delta N - \Delta G\\)

由于 Eq (16) 计算的是\\(G\\)的变化和\\(Y\\)的变化之间的关系，而\\(\Delta N, \Delta L\\) 分别与\\(\Delta Y^f， \Delta Y\\)相关，我们可以从\\(\Delta N=-\Delta L\\)，或者\\(w\Delta N=-w\Delta L\\)入手进行以下推导

\\[\begin{aligned}
w\Delta N &=-w\Delta L = -w \Delta L \frac{L}{Y^f}\frac{L}{Y^f}\frac{\Delta Y^f}{\Delta Y^f} \\\\[0.6em]
&= - \frac{wL}{Y^f}\frac{L}{Y^f}\frac{\Delta L}{\Delta Y^f}\Delta Y^f\\\\[0.6em]
&= -s_L^f \eta_L \Delta Y^f \\\\[0.6em]
&= -s_L^f \eta_L [\alpha(s_K - s_I) \Delta N - \Delta G]\\\\[0.6em]
\Rightarrow s_L^f \eta_L\Delta G &= [w+s_L^f \eta_L\alpha(s_K - s_I)] \Delta N
\end{aligned}\\]

由于\\(Y = \alpha N \Rightarrow \Delta Y = \alpha \Delta N\\)，\\(s_N = w/\alpha\\)，再以及结合以上推导，我们可以得到 Eq (16):

\\[\begin{aligned}
s_L^f \eta_L\Delta G &= [w+s_L^f \eta_L\alpha(s_K - s_I)] \frac{\Delta Y}{\alpha} \\\\[0.6em]
\Leftrightarrow s_L^f \eta_L\Delta G &= [s_N+s_L^f \eta_L(s_K - s_I)]\Delta Y \\\\[0.6em]
\frac{\Delta Y}{\Delta G} &= \frac{s_L^f \eta_L }{s_N+s_L^f \eta_L(s_K - s_I)}\\\\[0.6em]
&= \frac{s_L^f \eta_L/s_N }{1+s_L^f \eta_L(s_K - s_I)/s_N }
\end{aligned}\\]

## Equation (17), (18)

这一部分引入比例税率，假设 lump-sum tax 恒定，假设\\(N\\)恒定，我们可以通过 Public Finance Rules 以及生产函数和稳态情况下的 Euler equation 得到两组\\(\Delta Y, \Delta \tau, \Delta G\\)的式子，从而可以解出\\(\Delta G\\)分别与\\(\Delta Y, \Delta \tau\\)的关系，即增加政府支出如何影响经济增长和比例税率。因为我们主要关注稳态情况下的关系，我们将省略下标\\(t\\)。

由于假设 lump-sum tax 恒定，\\(\Delta \text{TR} = 0\\).对 Public Finance Rules 取全微分得到\\[\begin{align}\tau \Delta Y + Y \Delta \tau = \Delta G\end{align}\\]

接下来使用稳态情况下的 Euler Equation \\(\beta\bigl(1+(1-\tau)\frac{\partial F(\cdot)}{\partial K}-\delta_K \bigr) = 1\\)。

首先我们需要通过生产函数\\(Y = A K^{\theta_K}N^{\theta_N}\\)得到\\(\frac{\partial F(\cdot)}{\partial K}\\)：

\\[\frac{\partial F(\cdot)}{\partial K} = A \theta_K K^{\theta_K-1}N^{\theta_N} = \frac{A}{K} \theta_K K^{\theta_K}N^{\theta_N} = \frac{\theta_K Y}{K}\\]

代入 Euler Equation:

\\[\begin{aligned}
&\beta\bigl(1+(1-\tau)\frac{\theta_K Y}{K}-\delta_K \bigr) = 1 \\\\[0.6em]
\Leftrightarrow &K = \frac{\theta_K(1-\tau)}{\frac{1}{\beta} -1 + \delta_K}Y
\end{aligned}\\]

\\(Z:= \theta_K/[\frac{1}{\beta} -1 + \delta_K]\\)，我们可以将以上式子写成\\(K = Z(1-\tau)Y\\)。

将这个式子代入到生产函数中

\\[\begin{aligned}
Y &= A K^{\theta_K}N^{\theta_N} = A (Z(1-\tau)Y)^{\theta_K}N^{\theta_N}\\\\[0.6em]
\Rightarrow Y^{1-\theta_K} &= (1-\tau)^{\theta_K} AZ^{\theta_K}N^{\theta_N}\\\\[0.6em]
\Rightarrow (1-\theta_K)\log Y &= \theta_K \log (1-\tau)+ \log (AZ^{\theta_K}N^{\theta_N})\\\\[0.6em]
\Rightarrow (1-\theta_K)\log Y &= \theta_K \log (1-\tau)+ \log (AZ^{\theta_K}N^{\theta_N})\\\\[0.6em]
\Rightarrow \frac{\Delta Y}{Y} &= \Delta \log Y = \frac{\theta_K}{1-\theta_K} \frac{1}{1-\tau}(-\Delta \tau)\\\\[0.6em]
\Rightarrow \frac{\Delta Y}{\Delta \tau} &= -\frac{\theta_K}{1-\theta_K} \frac{1}{1-\tau}Y = -\frac{\theta_K}{\theta_N} \frac{1}{1-\tau}Y
\end{aligned}\\]

将这个式子代回(1)替换\\(\Delta \tau\\)将得到 Eq (17)，替换\\(\Delta Y\\)将得到 Eq (18)。

Eq (17): \\(\Delta Y = -\frac{\theta_K}{\theta_N-\tau}\Delta G\\)

\\[\begin{aligned}
\Delta \tau &= -\frac{\theta_N(1-\tau)}{\theta_K} \frac{\Delta Y}{Y}\\\\[0.6em]
\Rightarrow \Delta G &= \tau \Delta Y - Y \frac{\theta_N(1-\tau)}{\theta_K} \frac{\Delta Y}{Y} \\\\[0.6em]
\Rightarrow \Delta G &= (\tau - \frac{\theta_N(1-\tau)}{\theta_K}) \Delta Y \\\\[0.6em]
\Rightarrow \Delta G &= (\frac{\tau(\theta_K)-\theta_N(1-\tau)}{\theta_K}) \Delta Y \\\\[0.6em]
\Rightarrow \Delta G &= \frac{\tau(1-\theta_N)-\theta_N(1-\tau)}{\theta_K} \Delta Y \\\\[0.6em]
\Rightarrow \Delta Y &= -\frac{\theta_K}{\theta_N-\tau} \Delta Y \\\\[0.6em]
\end{aligned}\\]

Eq (18): \\(\Delta \tau = (1-\tau)\frac{\theta_N}{\theta_N-\tau}\frac{\Delta G}{Y}\\)

\\[\begin{aligned}
\Delta Y &= -\frac{\theta_K}{\theta_N(1-\tau)}Y \Delta \tau\\\\[0.6em]
\Rightarrow \Delta G &= Y \Delta \tau -\tau \frac{\theta_K}{\theta_N(1-\tau)}Y \Delta \tau \\\\[0.6em]
\Rightarrow \frac{\Delta G}{Y} &= (1 -\frac{\tau \theta_K}{\theta_N(1-\tau)})\Delta \tau\\\\[0.6em]
\Rightarrow \frac{\Delta G}{Y} &= \frac{\theta_N(1-\tau)-\tau(1-\theta_N)}{\theta_N(1-\tau)} \Delta \tau\\\\[0.6em]
\Rightarrow \frac{\Delta G}{Y} &= \frac{\theta_N-\tau}{\theta_N(1-\tau)}\Delta \tau\\\\[0.6em]
\Rightarrow \Delta \tau&= \frac{\theta_N(1-\tau)}{\theta_N-\tau}\frac{\Delta G}{Y}
\end{aligned}\\]
