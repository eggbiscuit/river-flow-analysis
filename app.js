// 处理视频上传和显示
document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("videoFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("请选择一个视频文件");
        return;
    }

    const loadingSpinner = document.getElementById("loadingSpinner");
    const videoElement = document.getElementById("processedVideo");
    const analysisTable = document.getElementById("analysisTable");

    try {
        // 显示加载动画
        loadingSpinner && (loadingSpinner.style.display = "block");
        videoElement.style.display = "none";
        analysisTable.style.display = "none";

        const formData = new FormData();
        formData.append("video", file);

        const response = await fetch("http://127.0.0.1:5001/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "上传失败");
        }

        const data = await response.json();

        // 设置视频的 src 并强制加载
        videoElement.src = `${data.output_video}?t=${Date.now()}`; // 防止缓存
        videoElement.load(); // 强制重新加载视频
        videoElement.style.display = "block"; // 确保视频可见

        // 加载分析结果
        await fetchAnalysis(data.video_id);
    } catch (error) {
        console.error("错误:", error.message);
        alert("视频上传或处理失败：" + error.message);
    } finally {
        // 隐藏加载动画
        loadingSpinner && (loadingSpinner.style.display = "none");
    }
});

// 加载分析结果
async function fetchAnalysis(videoId) {
    const analysisTable = document.getElementById("analysisTable");
    const tbody = analysisTable.querySelector("tbody");
    const regionSelector = document.getElementById("regionSelector");

    try {
        const response = await fetch(`http://127.0.0.1:5001/analyze/${videoId}`);
        if (!response.ok) {
            throw new Error("无法获取分析结果");
        }

        const data = await response.json();
        console.log("分析结果数据:", data); // 调试日志

        // 按区域分组数据
        const groupedData = groupByRegion(data.flow_distribution);

        // 填充区域选择器
        regionSelector.innerHTML = ""; // 清空选择器
        Object.keys(groupedData).forEach((region) => {
            const option = document.createElement("option");
            option.value = region;
            option.textContent = region;
            regionSelector.appendChild(option);
        });

        // 默认显示第一个区域的数据
        if (Object.keys(groupedData).length > 0) {
            displayRegionData(groupedData, Object.keys(groupedData)[0]);
        }

        // 监听区域选择器的变化
        regionSelector.addEventListener("change", (event) => {
            const selectedRegion = event.target.value;
            displayRegionData(groupedData, selectedRegion);
        });

        // 显示表格
        analysisTable.style.display = "table";
    } catch (error) {
        console.error("分析结果加载失败:", error.message);
    }
}

// 按区域分组数据
function groupByRegion(data) {
    const groupedData = {};
    data.forEach((entry) => {
        if (!groupedData[entry.region]) {
            groupedData[entry.region] = [];
        }
        groupedData[entry.region].push(entry);
    });
    return groupedData;
}

// 显示指定区域的数据
function displayRegionData(groupedData, region) {
    const tbody = document.getElementById("analysisTable").querySelector("tbody");
    tbody.innerHTML = ""; // 清空表格内容

    groupedData[region].forEach((entry, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${index + 1}</td> <!-- 序号 -->
            <td>${entry.speed.toFixed(6)}</td> <!-- 保留 6 位小数 -->
            <td>${entry.max_speed.toFixed(6)}</td> <!-- 保留 6 位小数 -->
            <td>${entry.direction}</td>
        `;
        tbody.appendChild(row);
    });
}
// 显示指定区域的数据
function displayRegionData(groupedData, region) {
    const tbody = document.getElementById("analysisTable").querySelector("tbody");
    tbody.innerHTML = ""; // 清空表格内容

    groupedData[region].forEach((entry, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${index + 1}</td> <!-- 序号 -->
            <td>${entry.speed.toFixed(6)}</td> <!-- 保留 6 位小数 -->
            <td>${entry.max_speed.toFixed(6)}</td> <!-- 保留 6 位小数 -->
            <td>${entry.direction}</td>
        `;
        tbody.appendChild(row);
    });
}

// 处理视频加载错误
function handleVideoError() {
    alert("视频加载失败，请检查视频文件或联系管理员！");
}