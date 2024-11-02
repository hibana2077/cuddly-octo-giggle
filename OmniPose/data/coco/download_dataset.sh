sudo apt update || apt update &&
sudo apt install wget curl unzip -y || apt install wget curl unzip -y &&

curl -O -q http://images.cocodataset.org/zips/train2017.zip &&

curl -O -q http://images.cocodataset.org/zips/val2017.zip &&

curl -O -q http://images.cocodataset.org/annotations/annotations_trainval2017.zip &&

mkdir -p annotations &&
mkdir -p images &&

unzip -q annotations_trainval2017.zip -d annotations &&

echo "Downloaded COCO 2017 dataset"