# coding:utf8

from PIL import Image
import os

def get_size(file):
    """
    获取文件大小-kb
    """
    size = os.path.getsize(file)
    return size / 1024

def get_outfile(infile, outfile=''):
    if outfile:
        return outfile
    dir,suffix = infile.split('.')[0],infile.split('.')[1]
    outfile = '{}c.{}'.format(dir, suffix)
    return outfile

def compress_image(infile, outfile='', mb=150, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    tmp_file = ''
    # 如果是png或者bmp图片格式就进行RGB转换
    if infile.endswith('png') or infile.endswith('bmp'):
        tmp_file = infile.split('.')[0]+'c.jpg'
        # tmp_file ： N1_1_compress.jpg
        im = Image.open(infile)
        im.convert('RGB').save(tmp_file, quality=70)
        infile = tmp_file
    
    o_size = get_size(infile)
    # print('图片大小kb:',o_size)
    # 第一次RGB转换后查看filename_compress.jpg(N1_1_compress.jpg)大小是否大于要求的大小,小于就直接返回文件名.
    if o_size <= mb:
        return infile
    # get_outfile(infile, outfile)中的输出文件为''
    outfile = get_outfile(infile, outfile)

    file_now = infile
    # 循环压缩，压缩到满足150kb以下为止.
    while o_size > mb:
        im = Image.open(file_now)
        im.convert('RGB').save(file_now, quality=70)
        ''' quality参数：
            保存图像的质量，值的范围从1（最差）到95（最佳）。 
            默认值为75，使用中应尽量避免高于95的值; 
            100会禁用部分JPEG压缩算法，并导致大文件图像质量几乎没有任何增益
        '''
        im = Image.open(file_now)
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(outfile)
        #
    # 如果是png或者bgm图片,第一次转换成jpg后还是大于150kb,就会生成c.jpg的tmp_file图片文件,然后删除临时文件.
    if tmp_file:
        os.remove(tmp_file)
    return outfile


# if __name__ == '__main__':
#     print(compress_image(r'2a79837781834956b028e0a0a91e0e5.jpg'))
#     # print(compress_image(r'./src_jpg.jpg'))
#     # print(compress_image(r'./src_png.png', './compress_png.jpg'))
#     # print(compress_image(r'./src_bmp.bmp', './compress_bmp.jpg'))
#     compress_image(path)



