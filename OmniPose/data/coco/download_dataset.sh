sudo apt install wget curl unzip -y || apt install wget curl unzip -y &&

curl -O -q http://images.cocodataset.org/zips/train2017.zip &&
unzip -d train2017 train2017.zip &&
rm train2017.zip &&

curl -O -q http://images.cocodataset.org/zips/val2017.zip &&
unzip -d val2017 val2017.zip &&
rm val2017.zip &&

curl -O -q http://images.cocodataset.org/annotations/annotations_trainval2017.zip &&
unzip -d annotations annotations_trainval2017.zip &&
rm annotations_trainval2017.zip &&

echo "Downloaded COCO 2017 dataset"