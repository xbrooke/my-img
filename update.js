const fs = require('fs');
const path = require('path');

// 设置图片文件夹和目标 JSON 文件路径
const imagesFolder = path.join(__dirname, 'img');
const jsonFilePath = path.join(__dirname, 'images.json');

// 读取文件夹内容
function scanImages(folder) {
    const result = {};
    
    fs.readdirSync(folder).forEach(subFolder => {
        const subFolderPath = path.join(folder, subFolder);
        
        // 检查是否为文件夹
        if (fs.statSync(subFolderPath).isDirectory()) {
            const images = fs.readdirSync(subFolderPath).filter(file => {
                return /\.(jpg|jpeg|png|gif|avif)$/i.test(file); // 过滤图片文件
            });
            result[subFolder] = images; // 保存文件夹及其图片
        }
    });
    
    return result;
}

// 更新 images.json 文件
function updateJsonFile(data) {
    fs.writeFileSync(jsonFilePath, JSON.stringify(data, null, 4), 'utf8');
}

// 主函数
function main() {
    const imagesData = scanImages(imagesFolder);
    updateJsonFile(imagesData);
    console.log('images.json 文件已更新！');
}

// 运行主函数
main();
