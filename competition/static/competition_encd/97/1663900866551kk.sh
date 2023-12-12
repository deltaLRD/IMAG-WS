mypid=$(netstat -apn|grep 3000|awk '{print $7}'|cut -d/ -f1);
echo $mypid
kill -9 $mypid
cd IMAG/IMAG/imag
conda activate imag001
python main.py
cd ../../../front/imag-home
npm run build
sed -i "s/__react_static_root__/react_static_root__/g" `grep -rl "__react_static_root__" ./dist`
sed -i "s/react_root//g" `grep -rl "/react_root" ./dist`
cd ./dist
cd templates/
mv __react_static_root__/ react_static_root__
cd vendors~react_static_root__/src/containers/
mv User~__react_static_root__ User~react_static_root__
cd ../../../../
git init
git add .
git config --global user.email 1018526304@qq.com
git config --global user.name "hj"
git commit -m "auto commit"
git remote add origin1 https://github.com/Njust-imag/Njust-imag.github.io.git
git remote add origin2 https://github.com/Njust-imag/imag-njust.github.io.git
cd ..
mv CHAME1 dist/CHAME
cd dist
git push -f origin1 master
cd ..
mv CHAME2 dist/CHAME
cd dist
git push -f origin2 master
