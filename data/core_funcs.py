import pygame


# định nghĩa các chức năng sử dụng

# chức năng đổi màu hình ảnh
def swap_color(img, old_c, new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf


# chức năng cắt hình ảnh
def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


# chức năng cân bằng hóa
def normalize(num, amt):
    if num > amt:
        num -= amt
    elif num < -amt:
        num += amt
    else:
        num = 0
    return num
