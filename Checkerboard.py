# -*- coding: utf-8 -*-

import os
import numpy as np
from osgeo import gdal
import cv2 as cv
import tkinter
import tkinter.filedialog
 
# 定义读取和保存图像的类
class Checkerboard:
 
    def load_image(self, filename,img_width,img_height):
        image = gdal.Open(filename)
        f_img_width = image.RasterXSize
        f_img_height = image.RasterYSize
        
        if img_width != -1:
            f_img_width = img_width
        if img_height != -1:
            f_img_height = img_height
 
        img_geotrans = image.GetGeoTransform()
        img_proj = image.GetProjection()
        img_data = image.ReadAsArray(0, 0, image.RasterXSize, image.RasterYSize,buf_xsize=f_img_width,buf_ysize=f_img_height)
 
        del image
 
        return img_proj, img_geotrans, img_data
 
    def write_image(self, filename, img_proj, img_geotrans, img_data):
        # 判断栅格数据类型
        if 'int8' in img_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in img_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32
 
        # 判断数组维度
        if len(img_data.shape) == 3:
            img_bands, img_height, img_width = img_data.shape
        else:
            img_bands, (img_height, img_width) = 1, img_data.shape
 
        # 创建文件
        driver = gdal.GetDriverByName('GTiff')
        image = driver.Create(filename, img_width, img_height, img_bands, datatype)      
        image.SetGeoTransform(img_geotrans)
        image.SetProjection(img_proj)
 
        if img_bands == 1:
            image.GetRasterBand(1).WriteArray(img_data)
        else:
            for i in range(img_bands):
                image.GetRasterBand(i+1).WriteArray(img_data[i])
 
        del image # 删除变量,保留数据
    def gray_process(self,gray, maxout = 255, minout = 0):
        high_value = np.percentile(gray, 98)#取得98%直方图处对应灰度
        low_value = np.percentile(gray, 2)#同理
        truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value) 
        processed_gray = ((truncated_gray - low_value)/(high_value - low_value)) * (maxout - minout)#线性拉伸嘛
        return np.uint8(processed_gray)
    def TwoPercentLinear(self,image, max_out=255, min_out=0):
        r=image[0,:,:]
        g = image[1,:,:]
        b = image[2,:,:]
        
        r_p = Checkerboard().gray_process(r)
        g_p = Checkerboard().gray_process(g)
        b_p = Checkerboard().gray_process(b)
        result = cv.merge((b_p, g_p, r_p))#合并处理后的三个波段
        return np.uint8(result)
    def grey_scale(self, image):
        #img_gray = cv.cvtColor(image,cv.COLOR_RGB2GRAY)
        if len(image.shape) == 3:
            return Checkerboard().TwoPercentLinear(image)               
        else:
            return Checkerboard().gray_process(image)
def FileOpen(text,text3):
    r = tkinter.filedialog.askopenfilename(title='remote sensing open tkinter',filetypes=[('TIF', '*.tif *.tiff'), ('All files', '*')])
    text.delete(1.0, "end")
    text.insert("insert", r)
    print(r)
    if text3 == None:
        return
    t1path = text.get(1.0, "end")[:-1]
    t1name = os.path.splitext(os.path.basename(t1path))[0]
    print(t1name)
    t3path = r'E:\20200526\2020018\paper\checkerfile\\'+ t1name + '_checker.tif'
    text3.delete(1.0, "end")
    text3.insert("insert", t3path)
    print(text3.get(1.0, "end"))

def FileSave(text):
    r = tkinter.filedialog.asksaveasfilename(title='remote sensing save tkinter',filetypes=[('TIF', '*.tif *.tiff'), ('All files', '*')])
    text.delete(1.0, "end")
    text.insert("insert", r)
    print(r)
    
def checker(img1,img2,out):
    ri1 = img1[:-1]
    ri2 = img2[:-1]
    outpath = out[:-1]
    img_proj1, img_geotrans1, img_data1 = Checkerboard().load_image(ri1,-1,-1)
    dst2 = gdal.Open(ri2) 
    img_geotrans2 = dst2.GetGeoTransform()
    sx = round(dst2.RasterXSize / (img_geotrans1[5] / img_geotrans2[5]))
    sy = round(dst2.RasterYSize / (img_geotrans1[1] / img_geotrans2[1]))
    img_proj2, img_geotrans2, img_data2 = Checkerboard().load_image(ri2,sx,sy)    
    del dst2
    dx = img_geotrans2[0] - img_geotrans1[0]
    dy = img_geotrans2[3] - img_geotrans1[3]
    oy = dx / img_geotrans1[1]
    ox = dy / img_geotrans1[5]
    print(ox)
    print(oy)
    #cv.namedWindow('input_image', cv.WINDOW_NORMAL)
    #cv.imshow('input_image', Checkerboard().grey_scale(img_data1))
    #cv.namedWindow('input_image2', cv.WINDOW_NORMAL)
    #cv.imshow('input_image2', Checkerboard().grey_scale(img_data2))
    
    #绘制棋盘格
    i1 = Checkerboard().grey_scale(img_data1)
    i2 = Checkerboard().grey_scale(img_data2)
    print(i1.shape)
    print(i2.shape)
    nw = round(i1.shape[0] / 6)
    nh = round(i1.shape[1] / 6)
    newimg = np.zeros([i2.shape[0], i2.shape[1], 3], np.uint8)
    for i in range(0,i2.shape[0]):
        for j in range(0,i2.shape[1]):
            if i2.shape == 2:
                newimg[i][j][0] = i2[i][j]
                newimg[i][j][1] = i2[i][j]
                newimg[i][j][2] = i2[i][j]
            else:
                newimg[i][j][0] = i2[i][j][0]
                newimg[i][j][1] = i2[i][j][1]
                newimg[i][j][2] = i2[i][j][2]

    for i in range(0,i1.shape[0]):
        for j in range(0,i1.shape[1]):
            flagi = round(i / nw)
            flagj = round(j / nh)
            if (flagi + flagj) % 2 == 0:
                ni = round(i - ox)
                nj = round(j - oy)
                if i1.shape == 2:
                    if ni < i2.shape[0] and nj < i2.shape[1] and ni >= 0 and nj >= 0: 
                        newimg[i][j][0] = i1[ni][nj]
                        newimg[i][j][1] = i1[ni][nj]
                        newimg[i][j][2] = i1[ni][nj]
                else:
                    if ni < i2.shape[0] and nj < i2.shape[1] and ni >= 0 and nj >= 0:
                        newimg[i][j][0] = i1[ni][nj][0]
                        newimg[i][j][1] = i1[ni][nj][1]
                        newimg[i][j][2] = i1[ni][nj][2]
            
    #cv.namedWindow('input_image3', cv.WINDOW_NORMAL)
    #cv.imshow('input_image3', i2)
    cv.imwrite(outpath, newimg)
    tkinter.messagebox.showinfo('提示','执行成功')
    #cv.waitKey(0)
    #cv.destroyAllWindows()

def closeWindow():
    ans = tkinter.messagebox.askyesno(title='Warning',message='Close the window?')
    if ans:
        root.destroy()
    else:
        return
        
if __name__ == '__main__':
    
    root = tkinter.Tk()
    lab1=tkinter.Label(root,text='输入配准后影像:')
    t1=tkinter.Text(root,width = 30,height = 1)
    button1 = tkinter.Button(root, text='File Open',
                             command=lambda : FileOpen(t1,t3))
    lab2=tkinter.Label(root,text='输入基准影像:')
    t2=tkinter.Text(root,width = 30,height = 1)
    button2 = tkinter.Button(root, text='File Open',
                             command=lambda : FileOpen(t2,None))
    lab3=tkinter.Label(root,text='棋盘格输出路径:')
    t3=tkinter.Text(root,width = 30,height = 1)
    button3 = tkinter.Button(root, text='File Save',
                             command=lambda : FileSave(t3))
    t1.insert("insert", r'E:\20200526\2020018\data\1\SJWzy3gf2.tif')
    t2.insert("insert", r'E:\20200526\2020018\data\1\yili3gf2.tif')
    
    button4 = tkinter.Button(root, text='执行',
                             command=lambda : checker(t1.get(1.0, "end"),t2.get(1.0, "end"),t3.get(1.0, "end")))
    button5 = tkinter.Button(root, text='取消',
                             command=closeWindow)
    lab1.grid(row=0, column=0)
    lab2.grid(row=1, column=0)
    lab3.grid(row=2, column=0)
    t1.grid(row=0, column=1)
    t2.grid(row=1, column=1)
    t3.grid(row=2, column=1)
    button1.grid(row=0, column=2)
    button2.grid(row=1, column=2)
    button3.grid(row=2, column=2)
    button4.grid(row=3, column=0)
    button5.grid(row=3, column=2)
    
    root.mainloop()
    # 图像分块
    
    
