from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QObject
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


# 按钮悬停和点击的高亮动画
def apply_hover_animation(button):
    animation = QPropertyAnimation(button, b"opacity")
    animation.setDuration(250)
    animation.setStartValue(0.8)  # 初始透明度
    animation.setEndValue(1.0)  # 悬停时全不透明
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.start()


# 页面切换淡入淡出动画
def apply_page_switch_animation(page: QWidget):
    # 设置透明度效果
    opacity_effect = QGraphicsOpacityEffect()
    page.setGraphicsEffect(opacity_effect)

    # 创建淡入动画
    fade_in = QPropertyAnimation(opacity_effect, b"opacity")
    fade_in.setDuration(300)
    fade_in.setStartValue(0)
    fade_in.setEndValue(1)
    fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # 运行动画
    fade_in.start()