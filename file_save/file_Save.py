import os


def save_File(module_name, file,file_name):
    base_dir = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_dir, module_name, 'static',module_name+'_encd', file_name)
    f = open(file_path.encode('utf-8'), 'wb')
    f.write(file.read())