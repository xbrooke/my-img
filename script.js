// 配置基础链接
const baseUrl = "https://h.xbrooke.cn"; // 替换为你的 Netlify 站点地址
const currentFolder = "example-folder"; // 动态替换为当前文件夹

// 示例图片数据
const images = ["1.avif", "2.avif", "3.avif", "4.avif", "5.avif"]; // 可通过 API 动态获取

// 动态生成图片展示内容
function updateImageContainer(images) {
    const imageContainer = document.getElementById('image-container');
    imageContainer.innerHTML = images.map(image => {
        const imageUrl = `${baseUrl}/img/${currentFolder}/${image}`;
        return `
            <div class="image-wrapper">
                <img src="${imageUrl}" alt="Image">
                <div class="button-group">
                    <button onclick="copyLink('${imageUrl}')">复制普通链接</button>
                    <button onclick="copyMarkdown('${imageUrl}')">复制Markdown</button>
                </div>
            </div>
        `;
    }).join('');
}

// 复制链接功能
function copyToClipboard(text, message) {
    navigator.clipboard.writeText(text).then(() => {
        alert(message || "链接已复制到剪贴板！");
    }).catch(() => {
        alert("复制失败，请手动复制！");
    });
}

function copyLink(url) {
    copyToClipboard(url, "普通链接已复制！");
}

function copyMarkdown(url) {
    const markdownLink = `![image](${url})`;
    copyToClipboard(markdownLink, "Markdown 链接已复制！");
}

// 初始化
updateImageContainer(images);
