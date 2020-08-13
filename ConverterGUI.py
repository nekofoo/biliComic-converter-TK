import json
import os
import time
import tkinter as tk
from zipfile import ZipFile
from shutil import rmtree
from tkinter import messagebox


class ConverterGUI:

    def __init__(self):
        window = tk.Tk()
        window.resizable(width=False, height=False)
        window.title('biliComic Converter')
        window.geometry('300x150')
        l = tk.Label(window, text='BiliComic Converter', font=('Arial', 12), width=30, height=2)
        l.pack()
        self.cid = tk.StringVar()
        self.cid.set("comicID")
        e = tk.Entry(window, textvariable=self.cid)
        e.pack()
        b = tk.Button(window, text="开始！", command=self.converter)
        b.pack()
        window.mainloop()

    def getpicDict(self, comicId, episodeId, indexDataFile):
        def unzip(file, target_dir):
            obj = ZipFile(file)
            obj.extractall(target_dir)

        def generateHashKey(comicId, episodeId):
            n = [None for i in range(8)]
            e = int(comicId)
            t = int(episodeId)
            n[0] = t
            n[1] = t >> 8
            n[2] = t >> 16
            n[3] = t >> 24
            n[4] = e
            n[5] = e >> 8
            n[6] = e >> 16
            n[7] = e >> 24
            for idx in range(8):
                n[idx] = n[idx] % 256
            return n

        def unhashContent(hashKey, indexData):
            for idx in range(len(indexData)):
                indexData[idx] ^= hashKey[idx % 8]
            return bytes(indexData)

        path = "./" + str(comicId) + "/" + str(episodeId)
        os.mkdir(path + "/temp")
        tempPath = path + "/temp"
        key = generateHashKey(comicId, episodeId)
        with open(indexDataFile, 'rb') as f:
            indexData = f.read()
            indexData = list(indexData)[9:]
        indexData = unhashContent(hashKey=key, indexData=indexData)
        with open(tempPath + '/index.zip', 'wb') as index:
            index.write(indexData)

        unzip(tempPath + '/index.zip', tempPath)
        json_file = tempPath + '/index.dat'
        picData = json.load(open(json_file))["pics"]
        picDict = {}
        n = 1
        for pic in picData:
            picName = os.path.basename(pic).replace('.png', '.png.view').replace('.jpg', '.jpg.view')
            picDict[picName] = str(n) + '.webp'
            n = n + 1
        rmtree(tempPath)

        return picDict

    def list_all_files(self, rootdir):
        import os
        _files = []
        list_file = os.listdir(rootdir)
        for i in range(0, len(list_file)):
            path = os.path.join(rootdir, list_file[i])
            if os.path.isdir(path):
                _files.extend(self.list_all_files(path))
            if os.path.isfile(path):
                _files.append(path)
        return _files

    def list_all_dirs(self, rootdir):
        import os
        _folders = []
        list_file = os.listdir(rootdir)
        for i in range(0, len(list_file)):
            path = os.path.join(rootdir, list_file[i])
            if os.path.isdir(path):
                _folders.append(path)
        return _folders

    def picMaker(self, entry):
        comicId = self.cid.get()
        episodeId = entry.split("\\", 1)[1]
        os.makedirs('./' + str(comicId) + '_C' + '/' + str(episodeId))
        indexDataFile = "./" + str(comicId) + "/" + str(episodeId) + "/index.dat"
        src_dir = "./" + str(comicId) + "/" + str(episodeId)  # 源文件目录地址
        files = self.list_all_files(src_dir)
        i = 0
        for item in files:
            file_name = item.split("\\", 1)
            files[i] = file_name[1]
            i = i + 1
        files.remove("index.dat")
        picName = self.getpicDict(comicId, episodeId, indexDataFile)
        for file in files:
            with open("./" + str(comicId) + "/" + str(episodeId) + "/" + file, "rb+") as pic:
                data = pic.read()
                data_after = data[9:]
                with open('./' + str(comicId) + '_C' + '/' + str(episodeId) + "/" + picName[file], "wb") as new_pic:
                    new_pic.write(data_after)

    def converter(self):
        start = time.time()
        comicId = self.cid.get()
        try:
            episodes = self.list_all_dirs('./' + str(comicId))
        except FileNotFoundError:
            messagebox.showerror(title='Hi', message=str(comicId) + ' DOES NOT EXIST')
            return
        if episodes == []:
            messagebox.showerror(title='Hi', message=str(comicId) + ' is not a comicID')
            return
        try:
            os.makedirs('./' + str(comicId) + '_C')
        except FileExistsError:
            if messagebox.askyesno(title='Hi', message=str(comicId) + ' EXISTS, convert again?'):
                rmtree('./' + str(comicId) + '_C')
                os.makedirs('./' + str(comicId) + '_C')
            else:
                return
        result = map(self.picMaker, episodes)
        try:
            while True:
                next(result)
        except StopIteration:
            print("done")
            pass
        end = time.time()
        print(end - start)


if __name__ == '__main__':
    ConverterGUI()
