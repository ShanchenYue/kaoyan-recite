# -*- coding: utf-8 -*-
"""生成数学 / 信号与系统填空题库 quiz/fill.json（自评模式）"""
import json, io, os

ITEMS = []
_n = [0]

def I(sub, q, a, tag=""):
    _n[0] += 1
    if "·" in sub:
        subject, chapter = sub.split("·", 1)
    else:
        subject, chapter = sub, sub
    ITEMS.append({"id": "f%03d" % _n[0], "subject": subject,
                  "sub": chapter, "q": q, "a": a, "tag": tag})

# ════════════════════════════════════════════════════════
#  信号与系统 · 拉普拉斯变换对
# ════════════════════════════════════════════════════════
S = "信号与系统·拉普拉斯变换对"
I(S, r"单位阶跃 $u(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=\frac{1}{j\omega}+\pi\delta(\omega)$；$L(s)=\frac{1}{s}$，$Re(s)>0$")
I(S, r"单位冲激 $\delta(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=1$；$L(s)=1$，全 $s$ 平面")
I(S, r"常数 $1$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=2\pi\delta(\omega)$；$L(s)=\frac{1}{s}$，$Re(s)>0$")
I(S, r"冲激偶 $\delta^{\prime}(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=j\omega$；$L(s)=s$，全 $s$ 平面")
I(S, r"单边指数信号 $e^{-at}u(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=\frac{1}{a+j\omega}$；$L(s)=\frac{1}{s+a}$，$Re(s)>-a$")
I(S, r"双边指数信号 $e^{-a|t|}$ 的傅里叶变换与双边拉普拉斯变换？",
  r"$F(\omega)=\frac{2a}{a^2+\omega^2}$；$L(s)=\frac{2a}{a^2-s^2}$，$-a<Re(s)<a$")
I(S, r"符号函数 $sgn(t)$ 的傅里叶变换与（单边）拉普拉斯变换？",
  r"$F(\omega)=\frac{2}{j\omega}$；单边 $L(s)=\frac{1}{s}$（$t>0$ 时 $sgn(t)=1$）")
I(S, r"矩形窗 $E\left[u\left(t+\frac{\tau}{2}\right)-u\left(t-\frac{\tau}{2}\right)\right]$ 的变换？",
  r"$F(\omega)=E\tau\,Sa\left(\frac{\omega\tau}{2}\right)$；$L(s)=\frac{E}{s}\left(e^{\frac{s\tau}{2}}-e^{-\frac{s\tau}{2}}\right)=\frac{2E}{s}sh\left(\frac{s\tau}{2}\right)$")
I(S, r"$t\,u(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=j\pi\delta^{\prime}(\omega)-\frac{1}{\omega^2}$；$L(s)=\frac{1}{s^2}$")
I(S, r"$t^2u(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=-\pi\delta^{\prime\prime}(\omega)+\frac{2j}{\omega^3}$；$L(s)=\frac{2}{s^3}$")
I(S, r"$t^3u(t)$ 的傅里叶变换与拉普拉斯变换？",
  r"$F(\omega)=-j\pi\delta^{\prime\prime\prime}(\omega)+\frac{6}{\omega^4}$；$L(s)=\frac{6}{s^4}$")
I(S, r"余弦信号 $\cos(\omega_1t)$ 的傅里叶变换？",
  r"$F(\omega)=\pi\left[\delta(\omega-\omega_1)+\delta(\omega+\omega_1)\right]$；双边拉普拉斯变换不存在（无公共收敛域）")
I(S, r"单边余弦 $\cos(\omega_1t)u(t)$ 的变换？",
  r"$F(\omega)=\frac{j\omega}{\omega_1^2-\omega^2}+\frac{\pi}{2}\left[\delta(\omega-\omega_1)+\delta(\omega+\omega_1)\right]$；$L(s)=\frac{s}{s^2+\omega_1^2}$")
I(S, r"正弦信号 $\sin(\omega_1t)$ 的傅里叶变换？",
  r"$F(\omega)=\frac{\pi}{j}\left[\delta(\omega-\omega_1)-\delta(\omega+\omega_1)\right]$；双边拉普拉斯变换不存在")
I(S, r"单边正弦 $\sin(\omega_1t)u(t)$ 的变换？",
  r"$F(\omega)=\frac{\omega_1}{\omega_1^2-\omega^2}+\frac{\pi}{2j}\left[\delta(\omega-\omega_1)-\delta(\omega+\omega_1)\right]$；$L(s)=\frac{\omega_1}{s^2+\omega_1^2}$")
I(S, r"周期冲激串 $\sum_{n=-\infty}^{\infty}\delta(t-nT_1)$ 的变换？",
  r"$F(\omega)=\frac{2\pi}{T_1}\sum_{n=-\infty}^{\infty}\delta\left(\omega-\frac{2n\pi}{T_1}\right)$；单边 $L(s)=\frac{1}{1-e^{-sT_1}}$，$Re(s)>0$")
I(S, r"双曲正弦 $sh(at)u(t)=\frac{e^{at}-e^{-at}}{2}u(t)$ 的变换？",
  r"$F(\omega)=-\frac{a}{a^2+\omega^2}$；$L(s)=\frac{a}{s^2-a^2}$，$Re(s)>|a|$")
I(S, r"双曲余弦 $ch(at)u(t)=\frac{e^{at}+e^{-at}}{2}u(t)$ 的变换？",
  r"$F(\omega)=-\frac{j\omega}{a^2+\omega^2}$；$L(s)=\frac{s}{s^2-a^2}$，$Re(s)>|a|$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 拉普拉斯变换性质
# ════════════════════════════════════════════════════════
S = "信号与系统·拉普拉斯变换性质"
I(S, r"拉普拉斯变换的线性性质？", r"$ax_1(t)+bx_2(t)\leftrightarrow aX_1(s)+bX_2(s)$，收敛域至少为两收敛域的交集；傅里叶变换同样成立")
I(S, r"拉普拉斯变换的尺度变换性质？", r"$x(at)\leftrightarrow\frac{1}{|a|}X\left(\frac{s}{a}\right)$，收敛域按 $|a|$ 缩放；傅里叶变换为 $\frac{1}{|a|}X\left(\frac{\omega}{a}\right)$")
I(S, r"拉普拉斯变换的时移性质？", r"$x(t-t_0)\leftrightarrow e^{-st_0}X(s)$；傅里叶变换为 $e^{-j\omega t_0}X(\omega)$")
I(S, r"拉普拉斯变换的频移性质？", r"$e^{s_0t}x(t)\leftrightarrow X(s-s_0)$；傅里叶变换为 $e^{j\omega_0t}x(t)\leftrightarrow X(\omega-\omega_0)$")
I(S, r"拉普拉斯变换的时域微分性质？", r"$x^{\prime}(t)\leftrightarrow sX(s)-x(0^-)$；傅里叶变换为 $x^{\prime}(t)\leftrightarrow j\omega X(\omega)$")
I(S, r"拉普拉斯变换的频域微分性质？", r"$-t\,x(t)\leftrightarrow\frac{dX(s)}{ds}$；傅里叶变换为 $-jt\,x(t)\leftrightarrow\frac{dX(\omega)}{d\omega}$")
I(S, r"拉普拉斯变换的时域积分性质？", r"$\int_{0}^{t}x(\tau)d\tau\leftrightarrow\frac{X(s)}{s}$（单边）；傅里叶为 $\int_{-\infty}^{t}x(\tau)d\tau\leftrightarrow\frac{X(\omega)}{j\omega}+\pi X(0)\delta(\omega)$")
I(S, r"拉普拉斯变换的频域积分性质？", r"$\frac{x(t)}{-jt}\leftrightarrow\int_{-\infty}^{\omega}X(\Omega)d\Omega$；对应拉氏形式为 $\frac{x(t)}{t}\leftrightarrow\int_{s}^{\infty}X(\sigma)d\sigma$")
I(S, r"拉普拉斯变换的终值定理及其使用条件？", r"$\lim_{t\to\infty}x(t)=\lim_{s\to0}sX(s)$；条件：$sX(s)$ 的极点全部位于左半平面（原点处至多一阶极点）")
I(S, r"拉普拉斯变换的初值定理及其使用条件？", r"$x(0^+)=\lim_{s\to\infty}sX(s)$；条件：$X(s)$ 为真分式（分子次数小于分母次数）")
I(S, r"拉普拉斯变换的时域卷积定理？", r"$x_1(t)*x_2(t)\leftrightarrow X_1(s)X_2(s)$，收敛域至少为两收敛域的交集")
I(S, r"拉普拉斯变换的时域相乘（复卷积）定理？", r"$x_1(t)x_2(t)\leftrightarrow\frac{1}{2\pi j}\int_{\sigma-j\infty}^{\sigma+j\infty}X_1(\lambda)X_2(s-\lambda)d\lambda$；傅里叶形式为 $\frac{1}{2\pi}X_1(\omega)*X_2(\omega)$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 电路元件 S 域模型
# ════════════════════════════════════════════════════════
S = "信号与系统·电路S域模型"
I(S, r"电阻 $R$ 的 S 域（复频域）模型？", r"$V(s)=R\,I(s)$，S 域阻抗 $Z_R=R$；时域为 $v(t)=R\,i(t)$")
I(S, r"电容 $C$ 的 S 域（复频域）模型？", r"$I(s)=sC\,V(s)-C\,v(0^-)$，即 $V(s)=\frac{1}{sC}I(s)+\frac{v(0^-)}{s}$；$Z_C=\frac{1}{sC}$，并带串联电压源 $\frac{v(0^-)}{s}$")
I(S, r"电感 $L$ 的 S 域（复频域）模型？", r"$V(s)=sL\,I(s)-L\,i(0^-)$；$Z_L=sL$，并带串联电压源 $L\,i(0^-)$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 傅里叶级数表示
# ════════════════════════════════════════════════════════
S = "信号与系统·傅里叶级数表示"
I(S, r"周期信号的三角函数形式傅里叶级数展开式？", r"$x(t)=\frac{a_0}{2}+\sum_{n=1}^{\infty}\left[a_n\cos(n\omega_1t)+b_n\sin(n\omega_1t)\right]$，$\omega_1=\frac{2\pi}{T}$")
I(S, r"周期信号的指数函数形式傅里叶级数展开式？", r"$x(t)=\sum_{k=-\infty}^{\infty}X_k e^{jk\omega_1t}$，$\omega_1=\frac{2\pi}{T}$")
I(S, r"周期信号的纯余弦形式傅里叶级数展开式？", r"$x(t)=A_0+\sum_{n=1}^{\infty}A_n\cos(n\omega_1t+\varphi_n)$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 连续傅里叶级数性质
# ════════════════════════════════════════════════════════
S = "信号与系统·傅里叶级数性质"
I(S, r"傅里叶级数的线性性质？", r"$ax(t)+by(t)\leftrightarrow a\,a_k+b\,b_k$")
I(S, r"傅里叶级数的时域共轭性质？", r"$x^*(t)\leftrightarrow a_{-k}^*$")
I(S, r"傅里叶级数的调制（频移）特性？", r"$x(t)e^{jM\omega_1t}\leftrightarrow a_{k-M}$")
I(S, r"傅里叶级数的反折特性？", r"$x(-t)\leftrightarrow a_{-k}$")
I(S, r"傅里叶级数的时移特性？", r"$x(t-t_0)\leftrightarrow a_k e^{-jk\omega_1t_0}$")
I(S, r"傅里叶级数的时域微分特性？", r"$\frac{dx(t)}{dt}\leftrightarrow jk\omega_1a_k$")
I(S, r"傅里叶级数的相乘特性？", r"$x(t)y(t)\leftrightarrow\sum_{l=-\infty}^{\infty}a_l b_{k-l}$（周期卷积）")
I(S, r"傅里叶级数的周期卷积特性？", r"$x(t)\circledast y(t)\leftrightarrow T\,a_kb_k$")
I(S, r"周期信号的功率与傅里叶系数的关系（帕塞瓦尔）？", r"$P=\frac{1}{T}\int_T|x(t)|^2dt=\sum_{k=-\infty}^{\infty}|a_k|^2$")
I(S, r"傅里叶级数的时域尺度变换特性？", r"$x(at)$ 的基频变为 $a\omega_1$，傅里叶系数 $a_k$ 保持不变（仅重新排列）")
I(S, r"实信号傅里叶系数的共轭对称性？", r"$a_{-k}=a_k^*$")
I(S, r"实偶信号的傅里叶系数特点？", r"$a_k$ 为实且偶，即 $a_k=a_{-k}$")
I(S, r"实奇信号的傅里叶系数特点？", r"$a_k$ 为纯虚且奇，即 $a_k=-a_{-k}$")
I(S, r"实信号奇偶分解对应的傅里叶系数？", r"$Ev\{x(t)\}\leftrightarrow Re\{a_k\}$，$Od\{x(t)\}\leftrightarrow j\,Im\{a_k\}$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 常见傅里叶级数
# ════════════════════════════════════════════════════════
S = "信号与系统·常见傅里叶级数"
I(S, r"$x(t)=\sum_{k=-\infty}^{\infty}a_k e^{jk\omega_0t}$ 的傅里叶级数系数？", r"即为 $a_k$（该展开式的系数本身就是 $a_k$）")
I(S, r"$e^{jk\omega_0t}$ 的傅里叶级数系数？", r"$a_k=1$（仅该次谐波），其余系数为 $0$")
I(S, r"$\cos(\omega_0t)$ 的傅里叶级数系数？", r"$a_1=a_{-1}=\frac{1}{2}$，其余为 $0$")
I(S, r"$\sin(\omega_0t)$ 的傅里叶级数系数？", r"$a_1=\frac{1}{2j}$，$a_{-1}=-\frac{1}{2j}$，其余为 $0$")
I(S, r"$x(t)=1$ 的傅里叶级数系数？", r"$a_0=1$，其余 $a_k=0$（$k\neq0$）")
I(S, r"周期矩形脉冲（幅度 1、脉宽 $2T_1$、周期 $T$）的傅里叶级数系数？", r"$a_k=\frac{2T_1}{T}Sa\left(k\omega_0T_1\right)$")
I(S, r"周期冲激串 $\sum_{n=-\infty}^{\infty}\delta(t-nT)$ 的傅里叶级数系数？", r"$a_k=\frac{1}{T}$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 傅里叶变换性质
# ════════════════════════════════════════════════════════
S = "信号与系统·傅里叶变换性质"
I(S, r"傅里叶变换的唯一性？", r"$f(t)$ 与 $F(\omega)$ 一一对应，变换对唯一")
I(S, r"傅里叶变换的线性性质？", r"$\sum_{i=1}^{n}A_if_i(t)\leftrightarrow\sum_{i=1}^{n}A_iF_i(\omega)$")
I(S, r"傅里叶变换的对偶性？", r"$F(t)\leftrightarrow 2\pi f(-\omega)$")
I(S, r"傅里叶变换的尺度变换特性？", r"$f(at)\leftrightarrow\frac{1}{|a|}F\left(\frac{\omega}{a}\right)$；$f(-t)\leftrightarrow F(-\omega)$")
I(S, r"傅里叶变换的时移特性？", r"$f(t-t_0)\leftrightarrow F(\omega)e^{-j\omega t_0}$；$f(at-t_0)\leftrightarrow\frac{1}{|a|}F\left(\frac{\omega}{a}\right)e^{-j\frac{\omega t_0}{a}}$")
I(S, r"傅里叶变换的频移特性？", r"$f(t)e^{\pm j\omega_0t}\leftrightarrow F(\omega\mp\omega_0)$")
I(S, r"余弦调制定理（$f(t)\cos\omega_0t$ 的频谱）？", r"$f(t)\cos(\omega_0t)\leftrightarrow\frac{1}{2}\left[F(\omega-\omega_0)+F(\omega+\omega_0)\right]$")
I(S, r"正弦调制定理（$f(t)\sin\omega_0t$ 的频谱）？", r"$f(t)\sin(\omega_0t)\leftrightarrow\frac{1}{2j}\left[F(\omega-\omega_0)-F(\omega+\omega_0)\right]$")
I(S, r"傅里叶变换的时域微分特性？", r"$\frac{df(t)}{dt}\leftrightarrow j\omega F(\omega)$，$\frac{d^kf(t)}{dt^k}\leftrightarrow(j\omega)^kF(\omega)$")
I(S, r"傅里叶变换的时域积分特性？", r"$\int_{-\infty}^{t}f(\tau)d\tau\leftrightarrow\frac{F(\omega)}{j\omega}+\pi F(0)\delta(\omega)$")
I(S, r"傅里叶变换的频域微分特性（时域乘 $t$）？", r"$(-jt)f(t)\leftrightarrow\frac{dF(\omega)}{d\omega}$，$(-jt)^kf(t)\leftrightarrow\frac{d^kF(\omega)}{d\omega^k}$")
I(S, r"傅里叶变换的频域积分特性？", r"$\pi f(0)\delta(t)-\frac{1}{jt}f(t)\leftrightarrow\int_{-\infty}^{\omega}F(\Omega)d\Omega$")
I(S, r"傅里叶变换的共轭特性？", r"$f^*(t)\leftrightarrow F^*(-\omega)$")
I(S, r"时域卷积定理？", r"$f_1(t)*f_2(t)\leftrightarrow F_1(\omega)F_2(\omega)$")
I(S, r"频域卷积定理？", r"$f_1(t)\,f_2(t)\leftrightarrow\frac{1}{2\pi}F_1(\omega)*F_2(\omega)$")
I(S, r"时域抽样（冲激抽样）的频谱？", r"$f(t)\sum_{n=-\infty}^{\infty}\delta(t-nT_s)\leftrightarrow\frac{1}{T_s}\sum_{n=-\infty}^{\infty}F(\omega-n\omega_s)$，$\omega_s=\frac{2\pi}{T_s}$")
I(S, r"交替周期冲激抽样的频谱？", r"$f(t)\sum_{n=-\infty}^{\infty}(-1)^n\delta(t-nT_s)\leftrightarrow\frac{1}{T_s}\sum_{n=-\infty}^{\infty}F\left(\omega-n\omega_s-\frac{\omega_s}{2}\right)$")
I(S, r"频域抽样的时域表达式？", r"$\frac{1}{\omega_s}\sum_{n=-\infty}^{\infty}f\left(t-\frac{2n\pi}{\omega_s}\right)\leftrightarrow\sum_{n=-\infty}^{\infty}F(n\omega_s)\delta(\omega-n\omega_s)$")
I(S, r"自相关函数的傅里叶变换？", r"$R(\tau)=f(\tau)*f^*(-\tau)\leftrightarrow|F(\omega)|^2$（能量谱）")
I(S, r"互相关函数的傅里叶变换？", r"$R_{21}(\tau)\leftrightarrow F_2(\omega)F_1^*(\omega)$，$R_{12}(\tau)\leftrightarrow F_1(\omega)F_2^*(\omega)$")
I(S, r"帕塞瓦尔定理（能量等式）？", r"$\int_{-\infty}^{\infty}|f(t)|^2dt=\frac{1}{2\pi}\int_{-\infty}^{\infty}|F(\omega)|^2d\omega$")

# ════════════════════════════════════════════════════════
#  信号与系统 · 常见傅里叶变换对
# ════════════════════════════════════════════════════════
S = "信号与系统·常见傅里叶变换对"
I(S, r"单位冲激 $\delta(t)$ 的傅里叶变换？", r"$F(\omega)=1$")
I(S, r"常数信号 $1$ 的傅里叶变换？", r"$F(\omega)=2\pi\delta(\omega)$")
I(S, r"单位阶跃 $u(t)$ 的傅里叶变换？", r"$F(\omega)=\frac{1}{j\omega}+\pi\delta(\omega)$")
I(S, r"符号函数 $sgn(t)$ 的傅里叶变换？", r"$F(\omega)=\frac{2}{j\omega}$")
I(S, r"$\frac{1}{\pi t}$ 的傅里叶变换？", r"$F(\omega)=-j\,sgn(\omega)$")
I(S, r"单边指数 $e^{-at}u(t)\,(a>0)$ 的傅里叶变换？", r"$F(\omega)=\frac{1}{a+j\omega}$")
I(S, r"门函数 $E\,G_\tau(t)$（幅度 $E$、宽度 $\tau$）的傅里叶变换？", r"$F(\omega)=E\tau\,Sa\left(\frac{\omega\tau}{2}\right)$")
I(S, r"三角信号 $E\,tri_\tau(t)$ 的傅里叶变换？", r"$F(\omega)=E\tau\,Sa^2\left(\frac{\omega\tau}{4}\right)$")
I(S, r"抽样函数 $Sa(\omega_0t)$ 的傅里叶变换？", r"$F(\omega)=\frac{\pi}{\omega_0}G_{2\omega_0}(\omega)$（门函数，宽 $2\omega_0$）")
I(S, r"$e^{j\omega_0t}$ 的傅里叶变换？", r"$F(\omega)=2\pi\delta(\omega-\omega_0)$")
I(S, r"周期冲激串 $\sum_{n=-\infty}^{\infty}\delta(t-nT)$ 的傅里叶变换？", r"$F(\omega)=\frac{2\pi}{T}\sum_{n=-\infty}^{\infty}\delta\left(\omega-\frac{2n\pi}{T}\right)$")
I(S, r"$\cos(\omega_0t)$ 的傅里叶变换？", r"$F(\omega)=\pi\left[\delta(\omega-\omega_0)+\delta(\omega+\omega_0)\right]$")
I(S, r"$\sin(\omega_0t)$ 的傅里叶变换？", r"$F(\omega)=\frac{\pi}{j}\left[\delta(\omega-\omega_0)-\delta(\omega+\omega_0)\right]$")
I(S, r"$t\,u(t)$ 的傅里叶变换？", r"$F(\omega)=j\pi\delta^{\prime}(\omega)-\frac{1}{\omega^2}$")
I(S, r"$\sin(\omega_0t)u(t)$ 的傅里叶变换？", r"$F(\omega)=\frac{\omega_0}{\omega_0^2-\omega^2}+\frac{\pi}{2j}\left[\delta(\omega-\omega_0)-\delta(\omega+\omega_0)\right]$")
I(S, r"$\cos(\omega_0t)u(t)$ 的傅里叶变换？", r"$F(\omega)=\frac{j\omega}{\omega_0^2-\omega^2}+\frac{\pi}{2}\left[\delta(\omega-\omega_0)+\delta(\omega+\omega_0)\right]$")
I(S, r"周期延拓 $\sum_{n=-\infty}^{\infty}x(t-nT)$ 的傅里叶变换？", r"$F(\omega)=\frac{2\pi}{T}\sum_{k=-\infty}^{\infty}X(k\omega_0)\delta(\omega-k\omega_0)$，$\omega_0=\frac{2\pi}{T}$")
I(S, r"高斯信号 $e^{-(t/\tau)^2}$ 的傅里叶变换？", r"$F(\omega)=\tau\sqrt{\pi}\,e^{-\left(\frac{\omega\tau}{2}\right)^2}$")
I(S, r"$\frac{1}{2}\left[\delta(t-1)+\delta(t+1)\right]$ 的傅里叶变换？", r"$F(\omega)=\cos\omega$")
I(S, r"$t$ 的傅里叶变换？", r"$F(\omega)=j2\pi\delta^{\prime}(\omega)$")
I(S, r"$|t|$ 的傅里叶变换？", r"$F(\omega)=-\frac{2}{\omega^2}$")

# ════════════════════════════════════════════════════════
#  信号与系统 · Z 变换对
# ════════════════════════════════════════════════════════
S = "信号与系统·Z变换对"
I(S, r"$\delta[n]$ 的 Z 变换与收敛域？", r"$X(z)=1$，全 $z$ 平面")
I(S, r"$u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{1}{1-z^{-1}}=\frac{z}{z-1}$，$|z|>1$")
I(S, r"$u[n-1]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z^{-1}}{1-z^{-1}}=\frac{1}{z-1}$，$|z|>1$")
I(S, r"$a^n u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{1}{1-az^{-1}}=\frac{z}{z-a}$，$|z|>|a|$")
I(S, r"$a^{n-1}u[n-1]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z^{-1}}{1-az^{-1}}=\frac{1}{z-a}$，$|z|>|a|$")
I(S, r"$n\,u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z^{-1}}{(1-z^{-1})^2}=\frac{z}{(z-1)^2}$，$|z|>1$")
I(S, r"$n^2u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z(z+1)}{(z-1)^3}$，$|z|>1$")
I(S, r"$\frac{n(n-1)}{2}u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z^{-1}}{(1-z^{-1})^3}=\frac{z}{(z-1)^3}$，$|z|>1$")
I(S, r"$\frac{n(n+1)}{2}u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z(2z-1)}{(z-1)^3}$，$|z|>1$")
I(S, r"$n\,a^{n-1}u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{1}{(1-az^{-1})^2}=\frac{z}{(z-a)^2}$，$|z|>|a|$")
I(S, r"$\frac{n(n-1)\cdots(n-m+1)}{m!}a^{n-m}u[n]$ 的 Z 变换？", r"$X(z)=\frac{z}{(z-a)^{m+1}}$，$|z|>|a|$")
I(S, r"$\delta[n-m]$ 的 Z 变换？", r"$X(z)=z^{-m}$，全 $z$ 平面（$z=0$ 或 $\infty$ 视 $m$ 而定）")
I(S, r"$-u[-n-1]$ 的双边 Z 变换与收敛域？", r"单边 $Z$ 变换为 $0$（$n\geq0$ 时为 $0$）；双边 $X(z)=\frac{z}{z-1}$，$|z|<1$")
I(S, r"$-a^n u[-n-1]$ 的双边 Z 变换与收敛域？", r"单边为 $0$；双边 $X(z)=\frac{z}{z-a}$，$|z|<|a|$")
I(S, r"$-n\,u[-n-1]$ 的双边 Z 变换与收敛域？", r"$X(z)=\frac{z}{(z-1)^2}$，$|z|<1$")
I(S, r"$-n\,a^{n-1}u[-n-1]$ 的双边 Z 变换与收敛域？", r"$X(z)=\frac{z}{(z-a)^2}$，$|z|<|a|$")
I(S, r"$-\frac{n(n-1)\cdots(n-m+1)}{m!}a^{n-m}u[-n-1]$ 的双边 Z 变换？", r"$X(z)=\frac{z}{(z-a)^{m+1}}$，$|z|<|a|$")
I(S, r"$\delta[n+m]$ 的 Z 变换？", r"$X(z)=z^{m}$，全 $z$ 平面")
I(S, r"$a^n u[n]-b^n u[-n-1]$（$|b|>|a|$）的 Z 变换与收敛域？", r"$X(z)=\frac{z}{z-a}-\frac{z}{z-b}$，$|a|<|z|<|b|$")
I(S, r"$\cos(\omega_0n)u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z(z-\cos\omega_0)}{z^2-2z\cos\omega_0+1}$，$|z|>1$")
I(S, r"$\sin(\omega_0n)u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z\sin\omega_0}{z^2-2z\cos\omega_0+1}$，$|z|>1$")
I(S, r"$\cos\left(\frac{\pi}{2}n\right)u[n]$ 的 Z 变换？", r"$X(z)=\frac{z^2}{z^2+1}$，$|z|>1$")
I(S, r"$\sin\left(\frac{\pi}{2}n\right)u[n]$ 的 Z 变换？", r"$X(z)=\frac{z}{z^2+1}$，$|z|>1$")
I(S, r"$r^n\cos(\omega_0n)u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{z(z-r\cos\omega_0)}{z^2-2rz\cos\omega_0+r^2}$，$|z|>r$")
I(S, r"$r^n\sin(\omega_0n)u[n]$ 的 Z 变换与收敛域？", r"$X(z)=\frac{zr\sin\omega_0}{z^2-2rz\cos\omega_0+r^2}$，$|z|>r$")
I(S, r"周期冲激串 $\sum_{m=0}^{\infty}\delta[n-mN]$ 的 Z 变换？", r"$X(z)=\frac{1}{1-z^{-N}}$，$|z|>1$")

# ════════════════════════════════════════════════════════
#  信号与系统 · Z 变换性质
# ════════════════════════════════════════════════════════
S = "信号与系统·Z变换性质"
I(S, r"Z 变换的线性性质？", r"$ax_1[n]+bx_2[n]\leftrightarrow aX_1(z)+bX_2(z)$，收敛域至少为两收敛域的交集")
I(S, r"Z 变换的时移性质？", r"$x[n-n_0]\leftrightarrow z^{-n_0}X(z)$，收敛域不变（$z=0$ 或 $\infty$ 可能例外）")
I(S, r"Z 变换的频域（z 域）尺度变换性质？", r"$z_0^n x[n]\leftrightarrow X\left(\frac{z}{z_0}\right)$，收敛域变为 $|z_0|R$")
I(S, r"Z 变换的时间反转性质？", r"$x[-n]\leftrightarrow X\left(\frac{1}{z}\right)$，收敛域变为 $\frac{1}{R}$")
I(S, r"Z 变换的时域拓展性质？", r"$x_{(k)}[n]\leftrightarrow X(z^k)$，收敛域为 $R^{1/k}$")
I(S, r"Z 变换的共轭性质？", r"$x^*[n]\leftrightarrow X^*(z^*)$，收敛域不变")
I(S, r"Z 变换的卷积定理？", r"$x_1[n]*x_2[n]\leftrightarrow X_1(z)X_2(z)$，收敛域至少为两收敛域的交集")
I(S, r"Z 变换的频域微分性质？", r"$n\,x[n]\leftrightarrow -z\frac{dX(z)}{dz}$")
I(S, r"Z 变换的初值定理？", r"若 $x[n]$ 为因果信号，则 $x[0]=\lim_{z\to\infty}X(z)$")
I(S, r"Z 变换的终值定理？", r"若 $x[n]$ 为因果信号且极点在单位圆内，则 $\lim_{n\to\infty}x[n]=\lim_{z\to1}(z-1)X(z)$")

# ════════════════════════════════════════════════════════
#  信号与系统 · DFT 性质
# ════════════════════════════════════════════════════════
S = "信号与系统·DFT性质"
I(S, r"DFT 的线性性质？", r"$a\,x[n]+b\,y[n]\leftrightarrow aX[k]+bY[k]$")
I(S, r"DFT 的时移性质（循环移位）？", r"$x[(n-n_0)_N]\leftrightarrow W_N^{kn_0}X[k]$，$W_N=e^{-j\frac{2\pi}{N}}$")
I(S, r"DFT 的频移性质？", r"$e^{j\frac{2\pi k_0n}{N}}x[n]\leftrightarrow X[(k-k_0)_N]$")
I(S, r"DFT 的共轭性质？", r"$x^*[n]\leftrightarrow X^*[(-k)_N]$")
I(S, r"DFT 的时间反转性质？", r"$x[(-n)_N]\leftrightarrow X[(-k)_N]$")
I(S, r"DFT 的循环卷积定理？", r"$x[n]\circledast y[n]\leftrightarrow X[k]Y[k]$")
I(S, r"DFT 的相乘（时域相乘）性质？", r"$x[n]y[n]\leftrightarrow\frac{1}{N}X[k]\circledast Y[k]$")
I(S, r"DFT 的时域差分性质？", r"$x[n]-x[n-1]\leftrightarrow(1-W_N^k)X[k]$")
I(S, r"DFT 的累加性质？", r"$\sum_{m=-\infty}^{n}x[m]\leftrightarrow\frac{X[k]}{1-W_N^k}$")
I(S, r"实信号 DFT 的共轭对称性？", r"$X[k]=X^*[(-k)_N]$")
I(S, r"实偶信号 DFT 的对称性？", r"$X[k]$ 为实偶序列")
I(S, r"实奇信号 DFT 的对称性？", r"$X[k]$ 为纯虚奇序列")
I(S, r"DFT 的帕塞瓦尔定理？", r"$\sum_{n=0}^{N-1}|x[n]|^2=\frac{1}{N}\sum_{k=0}^{N-1}|X[k]|^2$")

# ════════════════════════════════════════════════════════
#  数学 · 基本积分公式
# ════════════════════════════════════════════════════════
S = "数学·基本积分公式"
I(S, r"$\int ax\,dx=?$", r"$\frac{a}{2}x^2+C$")
I(S, r"$\int x^a\,dx=?$", r"$\frac{x^{a+1}}{a+1}+C$（$a\neq-1$）")
I(S, r"$\int\frac{1}{x}dx=?$", r"$\ln|x|+C$")
I(S, r"$\int e^x dx=?$", r"$e^x+C$")
I(S, r"$\int\sin x\,dx=?$", r"$-\cos x+C$")
I(S, r"$\int\cos x\,dx=?$", r"$\sin x+C$")
I(S, r"$\int a^x dx=?$", r"$\frac{a^x}{\ln a}+C$（$a>0,\ a\neq1$）")
I(S, r"$\int\frac{1}{\cos^2x}dx=?$", r"$\tan x+C$")
I(S, r"$\int\frac{1}{\sin^2x}dx=?$", r"$-\cot x+C$")
I(S, r"$\int\frac{1}{\sqrt{1-x^2}}dx=?$", r"$\arcsin x+C$")
I(S, r"$\int\frac{1}{1+x^2}dx=?$", r"$\arctan x+C$")
I(S, r"$\int\frac{1}{\sqrt{a^2-x^2}}dx=?$", r"$\arcsin\frac{x}{a}+C$")
I(S, r"$\int\frac{1}{a^2+x^2}dx=?$", r"$\frac{1}{a}\arctan\frac{x}{a}+C$")
I(S, r"$\int\frac{1}{1-x^2}dx=?$", r"$\frac{1}{2}\ln\left|\frac{1+x}{1-x}\right|+C$")
I(S, r"$\int\frac{1}{a^2-x^2}dx=?$", r"$\frac{1}{2a}\ln\left|\frac{a+x}{a-x}\right|+C$")
I(S, r"$\int\frac{1}{\cos x}dx=?$", r"$\ln\left|\sec x+\tan x\right|+C$")
I(S, r"$\int\frac{1}{\sin x}dx=?$", r"$\ln\left|\tan\frac{x}{2}\right|+C=\ln\left|\csc x-\cot x\right|+C$")
I(S, r"$\int\sqrt{a^2-x^2}\,dx=?$", r"$\frac{x}{2}\sqrt{a^2-x^2}+\frac{a^2}{2}\arcsin\frac{x}{a}+C$")
I(S, r"$\int\frac{1}{\sqrt{x^2\pm a^2}}dx=?$", r"$\ln\left|x+\sqrt{x^2\pm a^2}\right|+C$")

# ════════════════════════════════════════════════════════
#  数学 · 三角换元
# ════════════════════════════════════════════════════════
S = "数学·三角换元"
I(S, r"被积函数含 $\sqrt{a^2-x^2}$ 时如何换元？", r"令 $x=a\sin t$（$t\in[-\frac{\pi}{2},\frac{\pi}{2}]$），则 $\sqrt{a^2-x^2}=a\cos t$，$dx=a\cos t\,dt$")
I(S, r"被积函数含 $\sqrt{a^2+x^2}$ 时如何换元？", r"令 $x=a\tan t$（$t\in(-\frac{\pi}{2},\frac{\pi}{2})$），则 $\sqrt{a^2+x^2}=a\sec t$，$dx=a\sec^2t\,dt$")
I(S, r"被积函数含 $\sqrt{x^2-a^2}$ 时如何换元？", r"令 $x=a\sec t$，则 $\sqrt{x^2-a^2}=a\tan t$，$dx=a\sec t\tan t\,dt$")

# ════════════════════════════════════════════════════════
#  数学 · 含根式积分
# ════════════════════════════════════════════════════════
S = "数学·含根式积分"
I(S, r"$\int\sqrt{a^2-x^2}\,dx$ 用什么方法？", r"三角换元，令 $x=a\sin t$，化为 $\int a^2\cos^2t\,dt=\frac{a^2}{2}\left(t+\sin t\cos t\right)+C$")
I(S, r"$\int x\sqrt{a^2-x^2}\,dx$ 用什么方法？", r"凑微分，令 $u=a^2-x^2$，$du=-2x\,dx$，得 $-\frac{1}{3}\left(a^2-x^2\right)^{\frac{3}{2}}+C$")
I(S, r"$\int x^2\sqrt{a^2-x^2}\,dx$ 用什么方法？", r"三角换元，令 $x=a\sin t$，化为 $\int a^4\sin^2t\cos^2t\,dt$，再用倍角公式降次")
I(S, r"$\int x^3\sqrt{a^2-x^2}\,dx$ 用什么方法？", r"凑微分，令 $u=a^2-x^2$，把 $x^3dx=x^2\cdot x\,dx$ 写成 $\left(a^2-u\right)\cdot\left(-\frac{1}{2}\right)du$")
I(S, r"$\int\sqrt{2ax-x^2}\,dx$ 用什么方法？", r"先配方：$\sqrt{2ax-x^2}=\sqrt{a^2-(x-a)^2}$，再令 $x-a=a\sin t$ 做三角换元")

# ════════════════════════════════════════════════════════
#  数学 · 三角函数公式
# ════════════════════════════════════════════════════════
S = "数学·三角函数公式"
I(S, r"二倍角公式：$\sin2\varphi=?$", r"$2\sin\varphi\cos\varphi$")
I(S, r"二倍角公式：$\cos2\varphi=?$", r"$\cos^2\varphi-\sin^2\varphi=2\cos^2\varphi-1=1-2\sin^2\varphi$")
I(S, r"二倍角公式：$\tan2\varphi=?$", r"$\frac{2\tan\varphi}{1-\tan^2\varphi}$")
I(S, r"万能公式：用 $t=\tan\varphi$ 表示 $\sin2\varphi$", r"$\frac{2t}{1+t^2}$")
I(S, r"万能公式：用 $t=\tan\varphi$ 表示 $\cos2\varphi$", r"$\frac{1-t^2}{1+t^2}$")
I(S, r"万能公式：$\tan2\varphi=?$（用 $\tan\varphi$ 表示）", r"$\frac{2\tan\varphi}{1-\tan^2\varphi}$")
I(S, r"万能公式：$\cot2\varphi=?$（用 $\cot\varphi$ 表示）", r"$\frac{\cot^2\varphi-1}{2\cot\varphi}$")
I(S, r"和角公式：$\sin(\varphi+t)=?$", r"$\sin\varphi\cos t+\cos\varphi\sin t$")
I(S, r"差角公式：$\sin(\varphi-t)=?$", r"$\sin\varphi\cos t-\cos\varphi\sin t$")
I(S, r"和角公式：$\cos(\varphi+t)=?$", r"$\cos\varphi\cos t-\sin\varphi\sin t$")
I(S, r"差角公式：$\cos(\varphi-t)=?$", r"$\cos\varphi\cos t+\sin\varphi\sin t$")
I(S, r"和角公式：$\tan(\varphi+t)=?$", r"$\frac{\tan\varphi+\tan t}{1-\tan\varphi\tan t}$")
I(S, r"差角公式：$\tan(\varphi-t)=?$", r"$\frac{\tan\varphi-\tan t}{1+\tan\varphi\tan t}$")
I(S, r"积化和差：$\sin\varphi\cos t=?$", r"$\frac{1}{2}\left[\sin(\varphi+t)+\sin(\varphi-t)\right]$")
I(S, r"积化和差：$\cos\varphi\cos t=?$", r"$\frac{1}{2}\left[\cos(\varphi+t)+\cos(\varphi-t)\right]$")
I(S, r"积化和差：$\cos\varphi\sin t=?$", r"$\frac{1}{2}\left[\sin(\varphi+t)-\sin(\varphi-t)\right]$")
I(S, r"积化和差：$\sin\varphi\sin t=?$", r"$\frac{1}{2}\left[\cos(\varphi-t)-\cos(\varphi+t)\right]$")
I(S, r"和差化积：$\sin\varphi+\sin t=?$", r"$2\sin\frac{\varphi+t}{2}\cos\frac{\varphi-t}{2}$")
I(S, r"和差化积：$\sin\varphi-\sin t=?$", r"$2\cos\frac{\varphi+t}{2}\sin\frac{\varphi-t}{2}$")
I(S, r"和差化积：$\cos\varphi+\cos t=?$", r"$2\cos\frac{\varphi+t}{2}\cos\frac{\varphi-t}{2}$")
I(S, r"和差化积：$\cos\varphi-\cos t=?$", r"$-2\sin\frac{\varphi+t}{2}\sin\frac{\varphi-t}{2}$")
I(S, r"辅助角公式：$a\sin x+b\cos x=?$", r"$\sqrt{a^2+b^2}\,\sin(x+t)$，其中 $t$ 由 $\cos t=\frac{a}{\sqrt{a^2+b^2}}$ 确定")
I(S, r"辅助角公式中的 $\sin t=?$", r"$\frac{b}{\sqrt{a^2+b^2}}$")
I(S, r"辅助角公式中的 $\cos t=?$", r"$\frac{a}{\sqrt{a^2+b^2}}$")
I(S, r"辅助角公式中的 $\tan t=?$", r"$\frac{b}{a}$")
I(S, r"辅助角公式中的 $\cot t=?$", r"$\frac{a}{b}$")

# ════════════════════════════════════════════════════════
#  数学 · 等价无穷小
# ════════════════════════════════════════════════════════
S = "数学·等价无穷小（x→0）"
I(S, r"$x\to0$ 时，$\sin x=?$（等价无穷小）", r"$\sin x\sim x$；同理 $\tan x\sim x$，$\arcsin x\sim x$，$\arctan x\sim x$")
I(S, r"$x\to0$ 时，$\ln(1+x)\sim?$", r"$\ln(1+x)\sim x$")
I(S, r"$x\to0$ 时，$e^x-1\sim?$", r"$e^x-1\sim x$")
I(S, r"$x\to0$ 时，$a^x-1\sim?$", r"$a^x-1\sim x\ln a$")
I(S, r"$x\to0$ 时，$1-\cos x\sim?$", r"$1-\cos x\sim\frac{1}{2}x^2$")
I(S, r"$x\to0$ 时，$x-\sin x\sim?$", r"$x-\sin x\sim\frac{1}{6}x^3$")
I(S, r"$x\to0$ 时，$\tan x-x\sim?$", r"$\tan x-x\sim\frac{1}{3}x^3$")
I(S, r"$x\to0$ 时，$\arcsin x-x\sim?$", r"$\arcsin x-x\sim\frac{1}{6}x^3$")
I(S, r"$x\to0$ 时，$x-\arctan x\sim?$", r"$x-\arctan x\sim\frac{1}{3}x^3$")
I(S, r"$x\to0$ 时，$(1+x)^a-1\sim?$", r"$(1+x)^a-1\sim ax$")

# ════════════════════════════════════════════════════════
#  数学 · 两个重要极限
# ════════════════════════════════════════════════════════
S = "数学·重要极限"
I(S, r"$\lim_{x\to0}\frac{\sin x}{x}=?$", r"$1$")
I(S, r"$\lim_{n\to\infty}\left(1+\frac{1}{n}\right)^n=?$", r"$e$")
I(S, r"$\lim_{x\to\infty}\left(1+\frac{1}{x}\right)^x=?$", r"$e$")
I(S, r"$\lim_{x\to0}\left(1+x\right)^{\frac{1}{x}}=?$", r"$e$")

# ════════════════════════════════════════════════════════
#  数学 · 泰勒展开
# ════════════════════════════════════════════════════════
S = "数学·泰勒展开"
I(S, r"$e^x$ 的泰勒展开式？", r"$1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\cdots+\frac{x^n}{n!}+o(x^n)$")
I(S, r"$\sin x$ 的泰勒展开式？", r"$x-\frac{x^3}{3!}+\frac{x^5}{5!}-\cdots+(-1)^n\frac{x^{2n+1}}{(2n+1)!}+o(x^{2n+2})$")
I(S, r"$\cos x$ 的泰勒展开式？", r"$1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots+(-1)^n\frac{x^{2n}}{(2n)!}+o(x^{2n+1})$")
I(S, r"$\tan x$ 的泰勒展开式？", r"$x+\frac{x^3}{3}+\frac{2x^5}{15}+o(x^5)$")
I(S, r"$\ln(1+x)$ 的泰勒展开式？", r"$x-\frac{x^2}{2}+\frac{x^3}{3}-\cdots+(-1)^{n-1}\frac{x^n}{n}+o(x^n)$")
I(S, r"$\arctan x$ 的泰勒展开式？", r"$x-\frac{x^3}{3}+\frac{x^5}{5}-\cdots+(-1)^n\frac{x^{2n+1}}{2n+1}+o(x^{2n+2})$")
I(S, r"$\arcsin x$ 的泰勒展开式？", r"$x+\frac{x^3}{6}+\frac{3x^5}{40}+o(x^5)$")
I(S, r"$\frac{1}{1-x}$ 的展开式？", r"$1+x+x^2+x^3+\cdots+x^n+o(x^n)$，$|x|<1$")
I(S, r"$\frac{1}{1+x}$ 的展开式？", r"$1-x+x^2-x^3+\cdots+(-1)^nx^n+o(x^n)$，$|x|<1$")
I(S, r"$(1+x)^a$ 的泰勒展开式？", r"$1+ax+\frac{a(a-1)}{2!}x^2+\cdots+\frac{a(a-1)\cdots(a-n+1)}{n!}x^n+o(x^n)$")

# ════════════════════════════════════════════════════════
#  数学 · 导数定义 / 切线 / 法线
# ════════════════════════════════════════════════════════
S = "数学·导数与切线"
I(S, r"导数在 $x_0$ 处的定义式？", r"$f^{\prime}(x_0)=\lim_{\Delta x\to0}\frac{f(x_0+\Delta x)-f(x_0)}{\Delta x}=\lim_{x\to x_0}\frac{f(x)-f(x_0)}{x-x_0}$")
I(S, r"曲线 $y=f(x)$ 在点 $(x_0,f(x_0))$ 处的切线方程？", r"$y-f(x_0)=f^{\prime}(x_0)(x-x_0)$")
I(S, r"曲线 $y=f(x)$ 在点 $(x_0,f(x_0))$ 处的法线方程？", r"$y-f(x_0)=-\frac{1}{f^{\prime}(x_0)}(x-x_0)$（$f^{\prime}(x_0)\neq0$）")

# ════════════════════════════════════════════════════════
#  数学 · 常用导数
# ════════════════════════════════════════════════════════
S = "数学·常用导数公式"
I(S, r"$(c)^{\prime}=?$（$c$ 为常数）", r"$0$")
I(S, r"$(x^a)^{\prime}=?$", r"$a\,x^{a-1}$")
I(S, r"$(\sin x)^{\prime}=?$", r"$\cos x$")
I(S, r"$(\cos x)^{\prime}=?$", r"$-\sin x$")
I(S, r"$(\tan x)^{\prime}=?$", r"$\sec^2x=\frac{1}{\cos^2x}$")
I(S, r"$(\cot x)^{\prime}=?$", r"$-\csc^2x=-\frac{1}{\sin^2x}$")
I(S, r"$(\sec x)^{\prime}=?$", r"$\sec x\tan x$")
I(S, r"$(\csc x)^{\prime}=?$", r"$-\csc x\cot x$")
I(S, r"$(\log_a x)^{\prime}=?$", r"$\frac{1}{x\ln a}$")
I(S, r"$(\ln x)^{\prime}=?$", r"$\frac{1}{x}$")
I(S, r"$(a^x)^{\prime}=?$", r"$a^x\ln a$")
I(S, r"$(e^x)^{\prime}=?$", r"$e^x$")
I(S, r"$(\arcsin x)^{\prime}=?$", r"$\frac{1}{\sqrt{1-x^2}}$")
I(S, r"$(\arccos x)^{\prime}=?$", r"$-\frac{1}{\sqrt{1-x^2}}$")
I(S, r"$(\arctan x)^{\prime}=?$", r"$\frac{1}{1+x^2}$")
I(S, r"$(\text{arccot}\,x)^{\prime}=?$", r"$-\frac{1}{1+x^2}$")
I(S, r"$\left[\ln\left(x+\sqrt{x^2\pm a^2}\right)\right]^{\prime}=?$", r"$\frac{1}{\sqrt{x^2\pm a^2}}$")

# ════════════════════════════════════════════════════════
#  数学 · 高阶导数
# ════════════════════════════════════════════════════════
S = "数学·高阶导数"
I(S, r"$\left(x^\mu\right)^{(n)}=?$", r"$\mu(\mu-1)\cdots(\mu-n+1)x^{\mu-n}$")
I(S, r"$\left(a^x\right)^{(n)}=?$", r"$a^x(\ln a)^n$")
I(S, r"$\left[\sin(kx+b)\right]^{(n)}=?$", r"$k^n\sin\left(kx+b+\frac{n\pi}{2}\right)$")
I(S, r"$\left[\cos(kx+b)\right]^{(n)}=?$", r"$k^n\cos\left(kx+b+\frac{n\pi}{2}\right)$")
I(S, r"$\left[\ln(ax+b)\right]^{(n)}=?$", r"$(-1)^{n-1}(n-1)!\,\frac{a^n}{(ax+b)^n}$")
I(S, r"$\left(\frac{1}{ax+b}\right)^{(n)}=?$", r"$(-1)^n n!\,\frac{a^n}{(ax+b)^{n+1}}$")
I(S, r"莱布尼兹公式：$(uv)^{(n)}=?$", r"$\sum_{k=0}^{n}C_n^k\,u^{(n-k)}v^{(k)}$")

out = {"version": 1, "items": ITEMS}
os.makedirs(os.path.join(os.path.dirname(__file__), "quiz"), exist_ok=True)
p = os.path.join(os.path.dirname(__file__), "quiz", "fill.json")
with io.open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(x["sub"] for x in ITEMS)
print("total:", len(ITEMS))
for k, v in c.items():
    print("  %-32s %d" % (k, v))
print("->", p)
