<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>语文笔记生成器·AI智能版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { font-size: 16px; opacity: 0.9; }
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .input-group { margin-bottom: 15px; }
        .input-group input {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 5px;
        }
        .tip {
            font-size: 14px;
            color: #666;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        .tip.info { background: #fff3cd; color: #856404; }
        .tip.warning { background: #fff3cd; color: #856404; }
        .tip.success { background: #d4edda; color: #155724; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        #status { margin-top: 15px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🕷️ 语文笔记生成器·AI智能版</h1>
        <p>每次点击都重新爬取 + AI 重新生成 | 无缓存 | 强制刷新</p>
    </div>
    <div class="container">
        <div class="input-group">
            <input type="text" id="lessonName" placeholder="输入课文名，比如：海底世界">
        </div>
        <div class="input-group">
            <input type="text" id="lessonUrl" placeholder="如果自动搜索失败，手动填hanchacha的课文链接，比如：https://hanchacha.com/yuwen/xxx.html">
        </div>
        <div class="tip info">
            💡 如果自动搜索失败，可以手动在 hanchacha.com 找到课文链接填入上方
        </div>
        <div class="tip warning">
            ⚡ 每次点击都会重新爬取 hanchacha.com 并调用 AI 重新生成，不会使用旧笔记
        </div>
        <div class="tip success">
            ✅ GitHub Token 已配置，爬虫功能可用！每次都会重新生成。
        </div>
        <button onclick="generateNote()">🚀 重新生成笔记</button>
        <div id="status"></div>
    </div>

    <script>
        // 请修改这里的配置为你自己的信息
        const GITHUB_USERNAME =  "xiaoyu8906";
        const REPO_NAME = "yuwen-note";
        const GITHUB_TOKEN = "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";

        async function generateNote() {
            const lessonName = document.getElementById('lessonName').value.trim();
            const lessonUrl = document.getElementById('lessonUrl').value.trim();
            if (!lessonName) {
                alert("请输入课文名！");
                return;
            }

            const status = document.getElementById('status');
            status.textContent = "正在触发自动化流程，请稍候...";

            try {
                const response = await fetch(`https://api.github.com/repos/${GITHUB_USERNAME}/${REPO_NAME}/actions/workflows/crawl.yml/dispatches`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `token ${GITHUB_TOKEN}`,
                        'Accept': 'application/vnd.github.v3+json'
                    },
                    body: JSON.stringify({
                        ref: 'main',
                        inputs: {
                            lesson_name: lessonName,
                            lesson_url: lessonUrl
                        }
                    })
                });

                if (response.ok) {
                    status.textContent = `触发成功！正在为《${lessonName}》生成笔记，完成后会自动保存到仓库的data目录~`;
                } else {
                    status.textContent = "触发失败，请检查你的GitHub配置是否正确。";
                }
            } catch (e) {
                status.textContent = "出错了：" + e.message;
            }
        }
    </script>
</body>
</html>
