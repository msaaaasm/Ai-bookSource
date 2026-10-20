import json
import os
import sys

def build_book_source():
    # jsLib - 全局通用函数
    js_lib = """function getDomain() {
    var domain = "https://18comic.vip";
    try {
        var s = (typeof source !== 'undefined' && source) ? source : (this && this.source ? this.source : null);
        if (s && typeof s.getLoginInfoMap === 'function') {
            var info = s.getLoginInfoMap();
            if (info) {
                var custom = (info.get ? info.get("自定义域名") : null) || info["自定义域名"];
                if (custom && String(custom).trim()) {
                    domain = String(custom).trim();
                } else {
                    var preset = (info.get ? info.get("预设线路") : null) || info["预设线路"];
                    if (preset && String(preset).trim()) domain = String(preset).trim();
                }
            }
        }
    } catch(e) {}
    if (domain === "https://18comic.vip" && typeof baseUrl !== 'undefined' && baseUrl) {
        var m = String(baseUrl).match(/^(https?:\\/\\/[^\\/]+)/i);
        if (m && m[1]) {
            domain = m[1];
        }
    }
    domain = String(domain).trim().replace(/\\/+$/, '');
    if (!/^https?:\\/\\//i.test(domain)) {
        domain = "https://" + domain;
    }
    return domain;
}"""

    # loginUi - 登录界面布局
    login_ui = json.dumps([
        {
            "name": "内置网页登录",
            "type": "button",
            "action": "openLogin()",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 0.45 }
        },
        {
            "name": "Cloudflare过盾验证",
            "type": "button",
            "action": "verifyCloudflare()",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 0.45 }
        },
        {
            "name": "官方发布页 / 备用域名",
            "type": "button",
            "action": "openPublish('https://jmcomic.me')",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 1, "layout_wrapBefore": True }
        },
        {
            "name": "预设线路",
            "viewName": "'预设官方镜像线路'",
            "type": "select",
            "chars": [
                "https://18comic.vip",
                "https://18comic.org",
                "https://jmcomic.me",
                "https://18comic-vip.art"
            ],
            "default": "https://18comic.vip",
            "style": { "layout_flexGrow": 1, "layout_wrapBefore": True }
        },
        {
            "name": "自定义域名",
            "viewName": "'自定义域名 (从发布页复制粘贴，优先于预设)'",
            "type": "text",
            "default": "",
            "style": { "layout_flexGrow": 1, "layout_wrapBefore": True }
        },
        {
            "name": "填入预设到输入框",
            "type": "button",
            "action": "applyPreset()",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 0.45, "layout_wrapBefore": True }
        },
        {
            "name": "测试当前域名延迟",
            "type": "button",
            "action": "testDomain()",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 0.45 }
        },
        {
            "name": "保存并生效域名",
            "type": "button",
            "action": "saveDomain()",
            "style": { "layout_flexGrow": 1, "layout_flexBasisPercent": 1, "layout_wrapBefore": True }
        }
    ], ensure_ascii=False, indent=2)

    # loginUrl - 登录与线路切换逻辑
    login_url = """<js>
function getActiveDomain() {
    var domain = "";
    if (typeof result !== 'undefined' && result) {
        var custom = (result.get ? result.get("自定义域名") : result["自定义域名"]);
        if (custom && String(custom).trim()) {
            domain = String(custom).trim();
        } else {
            var preset = (result.get ? result.get("预设线路") : result["预设线路"]);
            if (preset && String(preset).trim()) domain = String(preset).trim();
        }
    }
    if (!domain) {
        if (typeof getDomain === 'function') domain = getDomain();
        else domain = "https://18comic.vip";
    }
    domain = String(domain).trim().replace(/\\/+$/, '');
    if (!/^https?:\\/\\//i.test(domain)) {
        domain = "https://" + domain;
    }
    return domain;
}

function openLogin() {
    var domain = getActiveDomain();
    if (typeof java !== 'undefined') {
        if (typeof java.startBrowser === 'function') {
            java.startBrowser(domain + "/login", "禁漫天堂 - 账号登录");
        } else if (typeof java.showBrowser === 'function') {
            java.showBrowser(domain + "/login");
        }
    }
}

function verifyCloudflare() {
    var domain = getActiveDomain();
    if (typeof java !== 'undefined') {
        if (typeof java.startBrowser === 'function') {
            java.startBrowser(domain + "/", "禁漫天堂 - Cloudflare人机验证");
        } else if (typeof java.showBrowser === 'function') {
            java.showBrowser(domain + "/");
        }
    }
}

function openPublish(url) {
    if (typeof java !== 'undefined') {
        if (typeof java.startBrowser === 'function') {
            java.startBrowser(url, "禁漫天堂 - 官方发布页");
        } else if (typeof java.showBrowser === 'function') {
            java.showBrowser(url);
        }
    }
}

function applyPreset() {
    var p = "";
    if (typeof result !== 'undefined' && result) {
        p = (result.get ? result.get("预设线路") : result["预设线路"]) || "";
    }
    if (!p) p = "https://18comic.vip";
    if (typeof java !== 'undefined') {
        if (typeof java.upLoginData === 'function') {
            try {
                var m = new java.util.HashMap();
                m.put("自定义域名", p);
                java.upLoginData(m);
            } catch(e) {
                java.upLoginData({"自定义域名": p});
            }
        }
        if (typeof java.toast === 'function') {
            java.toast("已填入预设线路:\\n" + p);
        }
    }
}

function testDomain() {
    var domain = getActiveDomain();
    if (typeof java !== 'undefined' && typeof java.ajax === 'function') {
        if (typeof java.toast === 'function') {
            java.toast("正在测试连接: " + domain + " ...");
        }
        try {
            var t0 = new Date().getTime();
            var res = java.ajax(domain + "/search/photos?search_query=test");
            var t1 = new Date().getTime();
            if (res && (res.indexOf("list-col") !== -1 || res.indexOf("video-title") !== -1 || res.indexOf("18comic") !== -1)) {
                if (typeof java.toast === 'function') {
                    java.toast("连接成功！响应延迟: " + (t1 - t0) + "ms\\n" + domain);
                }
            } else {
                if (typeof java.toast === 'function') {
                    java.toast("响应异常或需要过盾，建议更换镜像线路或点击过盾验证");
                }
            }
        } catch(e) {
            if (typeof java.toast === 'function') {
                java.toast("连接失败: " + e.message + "\\n请更换发布页提供的最新可用域名");
            }
        }
    }
}

function saveDomain() {
    var domain = getActiveDomain();
    var s = (typeof source !== 'undefined' && source) ? source : (this && this.source ? this.source : null);
    if (s && typeof s.putLoginInfo === 'function') {
        var saveObj = {
            "预设线路": domain,
            "自定义域名": domain
        };
        try {
            s.putLoginInfo(JSON.stringify(saveObj));
        } catch(e) {}
    }
    if (s && typeof s.setBookSourceUrl === 'function') {
        try {
            s.setBookSourceUrl(domain);
        } catch(e) {}
    }
    if (typeof java !== 'undefined') {
        if (typeof java.refreshExplore === 'function') {
            java.refreshExplore();
        }
        if (typeof java.toast === 'function') {
            java.toast("域名设置成功并已生效:\\n" + domain);
        }
    }
    return true;
}

function login() {
    return saveDomain();
}
</js>"""

    # exploreUrl - 发现大厅 (使用禁漫天堂真实 web 路由 /albums，全部配合 webView:true)
    explore_items = [
        { "title": "🏆 热门榜单", "url": "", "style": { "layout_flexGrow": 1, "layout_wrapBefore": True } },
        { "title": "今日热门", "url": "/albums?o=mv&t=t&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "本周热门", "url": "/albums?o=mv&t=w&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "本月热门", "url": "/albums?o=mv&t=m&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "历史总榜", "url": "/albums?o=mv&t=a&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },

        { "title": "✨ 综合排序", "url": "", "style": { "layout_flexGrow": 1, "layout_wrapBefore": True } },
        { "title": "最新上传", "url": "/albums?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "最多爱心", "url": "/albums?o=mp&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "最多收藏", "url": "/albums?o=tf&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "最多评论", "url": "/albums?o=md&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "最高评分", "url": "/albums?o=tr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },

        { "title": "📖 分类专区", "url": "", "style": { "layout_flexGrow": 1, "layout_wrapBefore": True } },
        { "title": "同人誌", "url": "/albums/doujin?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "單行本", "url": "/albums/single?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "短篇", "url": "/albums/short?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "韓漫", "url": "/albums/hanman?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "美漫", "url": "/albums/meiman?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "3D漫畫", "url": "/albums/3d?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "Cosplay", "url": "/albums/doujin_cosplay?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } },
        { "title": "其他漫畫", "url": "/albums/another?o=mr&page={{page}},{\"webView\":true}", "style": { "layout_flexGrow": 1 } }
    ]
    explore_url = json.dumps(explore_items, ensure_ascii=False, indent=2)

    # ruleBookInfo.intro - 简介 + 读者最新评论
    intro_rule = """<js>
result = (function() {
    var raw = (result ? result.toString() : (src ? src.toString() : ""));
    var aidMatch = baseUrl.match(/\/album\/(\\d+)/);
    var aid = aidMatch ? aidMatch[1] : "";

    // 1. 提取作品基本信息
    var headerLine = [];
    if (aid) headerLine.push("🆔【本子番号】 " + aid);
    var mDate = raw.match(/class="[^"]*float-left[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i) || raw.match(/日期[：:]?\\s*([^<\\s]+)/i);
    if (mDate) headerLine.push("📅【更新日期】 " + mDate[1].replace(/<[^>]+>/g, "").replace(/日期[：:]?/g, "").trim());
    var mLikes = raw.match(/class="[^"]*float-right[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i) || raw.match(/class="[^"]*train-number[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i);
    if (mLikes) headerLine.push("❤️【点赞热度】 " + mLikes[1].replace(/<[^>]+>/g, "").trim());

    // 2. 提取标签
    var tags = [];
    var tagMatches = raw.match(/data-type="tags"[^>]*>([\\s\\S]*?)<\\/span>/gi) || raw.match(/class="tag"[^>]*>([\\s\\S]*?)<\\/a>/gi);
    if (tagMatches) {
        for (var i = 0; i < tagMatches.length; i++) {
            var t = tagMatches[i].replace(/<[^>]+>/g, "").trim();
            if (t && tags.indexOf(t) === -1) tags.push(t);
        }
    }

    // 3. 提取简介叙述
    var desc = "";
    var mDesc = raw.match(/class="[^"]*intro-collapse-content[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i) || raw.match(/class="[^"]*p-t-5\\s+p-b-5[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i);
    if (mDesc) {
        desc = mDesc[1].replace(/<br\\s*\\/?>/gi, "\\n").replace(/<[^>]+>/g, "").replace(/叙述：|敘述：/g, "").trim();
    }

    var parts = [];
    if (headerLine.length > 0) parts.push(headerLine.join("      "));
    if (tags.length > 0) parts.push("🏷️【作品标签】\\n" + tags.join(", "));
    if (desc) parts.push("📖【作品叙述】\\n" + desc);
    else parts.push("📖【作品叙述】\\n暂无详细作品叙述。");

    // 4. 提取读者最新评论
    var comments = [];
    var commentBlocks = raw.split(/id="comment-\\d+"/i);
    if (commentBlocks.length > 1) {
        for (var j = 1; j < commentBlocks.length && comments.length < 8; j++) {
            var cb = commentBlocks[j];
            var mUser = cb.match(/class="[^"]*username[^"]*"[^>]*>([\\s\\S]*?)<\\/a>/i) || cb.match(/<strong[^>]*>([\\s\\S]*?)<\\/strong>/i);
            var mTime = cb.match(/class="[^"]*date[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i) || cb.match(/class="[^"]*pull-right[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i);
            var mText = cb.match(/class="[^"]*comment-content[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i) || cb.match(/class="[^"]*comment-body[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i);

            var u = mUser ? mUser[1].replace(/<[^>]+>/g, "").trim() : "书友";
            var t = mTime ? mTime[1].replace(/<[^>]+>/g, "").trim() : "";
            var c = mText ? mText[1].replace(/<[^>]+>/g, "").trim() : "";
            if (c) {
                var timeStr = t ? (" [" + t + "]") : "";
                comments.push("💬 【" + u + "】" + timeStr + "：\\n  " + c);
            }
        }
    }

    if (comments.length > 0) {
        parts.push("━━━━━━━━━━━━━━━━━━━━━\\n☕【读者热评 (" + comments.length + "条)】\\n\\n" + comments.join("\\n\\n"));
    } else {
        parts.push("━━━━━━━━━━━━━━━━━━━━━\\n☕【读者热评】\\n暂无抓取到直接评论，可在目录中点击「💬 读者讨论与精彩评论」查看完整留言区。");
    }

    return parts.join("\\n\\n");
})();
result;
</js>"""

    # ruleToc.chapterList - 目录提取（单话短篇、多话合集 + 评论区专享章节）
    toc_js = """<js>
var list = [];
(function() {
    var rawHtml = (result ? result.toString() : (src ? src.toString() : ""));
    var aidMatch = baseUrl.match(/\/album\/(\\d+)/);
    var aid = aidMatch ? aidMatch[1] : "";
    var domain = (baseUrl && baseUrl.match(/^https?:\\/\\/[^\\/]+/i)) ? baseUrl.match(/^https?:\\/\\/[^\\/]+/i)[0] : getDomain();

    // 1. 匹配多章节合集 (过滤重复的开始阅读/继续阅读按钮)
    var epRegex = /<a[^>]*href="([^"]*\\/photo\\/\\d+[^"]*)"[^>]*>([\\s\\S]*?)<\\/a>/gi;
    var match;
    var seen = {};
    var count = 0;
    while ((match = epRegex.exec(rawHtml)) !== null) {
        var href = match[1].trim();
        var rawName = match[2].replace(/<[^>]+>/g, "").trim();
        if (rawName === "开始阅读" || rawName === "開始閱讀" || rawName === "继续阅读" || rawName === "繼續閱讀") {
            continue;
        }
        if (href.indexOf("/photo/") !== -1 && !seen[href]) {
            seen[href] = true;
            count++;
            var name = rawName || ("第 " + count + " 话");
            var fullUrl = href.startsWith("http") ? href : (domain + href);
            fullUrl += ',{"webView":true}';
            list.push({
                title: name,
                name: name,
                url: fullUrl,
                link: fullUrl
            });
        }
    }

    // 2. 单话短篇/开始阅读适配 (当只有1话且没有单独的话次列表时)
    if (list.length === 0) {
        var mRead = rawHtml.match(/<a\\b[^>]*?\\bhref="([^"]*\\/photo\\/\\d+[^"]*)"[^>]*>/i);
        var readHref = mRead ? mRead[1].trim() : "";
        if (readHref) {
            var fullReadUrl = readHref.startsWith("http") ? readHref : (domain + readHref);
            fullReadUrl += ',{"webView":true}';
            list.push({
                title: "全一话",
                name: "全一话",
                url: fullReadUrl,
                link: fullReadUrl
            });
        }
    }

    // 3. 评论专享章节：方便读者直接在阅读正文中查看读者留言讨论
    if (aid) {
        list.push({
            title: "💬 读者讨论与精彩评论",
            name: "💬 读者讨论与精彩评论",
            url: domain + "/album/" + aid + "#comments",
            link: domain + "/album/" + aid + "#comments"
        });
    }
})();
result = list;
body = result;
result;
</js>"""

    # ruleContent.content - 正文提取（鲁棒提取 data-original / data-src / src，自动补全域名）
    content_js = """<js>
result = (function() {
    var str = (result ? result.toString() : (src ? src.toString() : ""));
    var domain = (baseUrl && baseUrl.match(/^https?:\\/\\/[^\\/]+/i)) ? baseUrl.match(/^https?:\\/\\/[^\\/]+/i)[0] : getDomain();
    
    // 1. 评论区专属章节处理
    if (baseUrl.indexOf('#comments') !== -1) {
        var aidMatch = baseUrl.match(/\/album\/(\\d+)/);
        var aid = aidMatch ? aidMatch[1] : "";
        var comments = [];
        var commentBlocks = str.split(/id="comment-\\d+"/i);
        if (commentBlocks.length > 1) {
            for (var j = 1; j < commentBlocks.length; j++) {
                var cb = commentBlocks[j];
                var mUser = cb.match(/class="[^"]*username[^"]*"[^>]*>([\\s\\S]*?)<\\/a>/i) || cb.match(/<strong[^>]*>([\\s\\S]*?)<\\/strong>/i);
                var mTime = cb.match(/class="[^"]*date[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i) || cb.match(/class="[^"]*pull-right[^"]*"[^>]*>([\\s\\S]*?)<\\/span>/i);
                var mText = cb.match(/class="[^"]*comment-content[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i) || cb.match(/class="[^"]*comment-body[^"]*"[^>]*>([\\s\\S]*?)<\\/div>/i);

                var u = mUser ? mUser[1].replace(/<[^>]+>/g, "").trim() : "热心书友";
                var t = mTime ? mTime[1].replace(/<[^>]+>/g, "").trim() : "";
                var c = mText ? mText[1].replace(/<br\\s*\\/?>/gi, "<br>").replace(/<[^>]+>/g, "").trim() : "";
                if (c) {
                    comments.push({ user: u, time: t, content: c });
                }
            }
        }

        var html = [];
        html.push('<div style="padding: 16px; font-family: sans-serif; line-height: 1.6; color: #2c3e50;">');
        html.push('<div style="border-bottom: 2px solid #e91e63; padding-bottom: 10px; margin-bottom: 16px;">');
        html.push('<h2 style="margin: 0; color: #e91e63; font-size: 20px;">💬 禁漫天堂 · 读者留言板</h2>');
        html.push('<div style="font-size: 13px; color: #888; margin-top: 4px;">本子番号 ID: ' + aid + ' | 共收录 ' + comments.length + ' 条近期热评</div>');
        html.push('</div>');

        if (comments.length > 0) {
            for (var k = 0; k < comments.length; k++) {
                var item = comments[k];
                html.push('<div style="margin-bottom: 14px; padding: 12px; background: #fdf2f4; border-radius: 8px; border-left: 4px solid #e91e63;">');
                html.push('<div style="font-weight: bold; color: #333; font-size: 14px;">' + item.user + ' <span style="font-weight: normal; font-size: 12px; color: #999; margin-left: 8px;">' + item.time + '</span></div>');
                html.push('<div style="margin-top: 6px; font-size: 14px; color: #444;">' + item.content + '</div>');
                html.push('</div>');
            }
        } else {
            html.push('<div style="text-align: center; padding: 40px 20px; color: #999;">');
            html.push('<p style="font-size: 16px;">暂无抓取到公开评论</p>');
            html.push('<p style="font-size: 13px;">部分评论需要登录账号后才向客户端展示。<br>您可以在书源菜单中点击「内置网页登录」登录您的禁漫账号。</p>');
            html.push('</div>');
        }
        html.push('</div>');
        return html.join('\\n');
    }

    // 2. 漫画图片提取 (解析所有 img 标签，逐个提取 data-original / data-src / src)
    var urls = [];
    var seen = {};
    var imgTags = str.match(/<img\\b[^>]+>/gi) || [];
    for (var i = 0; i < imgTags.length; i++) {
        var tag = imgTags[i];
        var mUrl = tag.match(/\\b(?:data-original|data-src)="([^"]+)"/i) || tag.match(/\\bsrc="([^"]+)"/i);
        if (mUrl && mUrl[1]) {
            var rawU = mUrl[1].trim();
            if (rawU.indexOf("media/photos") !== -1 || rawU.indexOf("photos/") !== -1) {
                var u = rawU;
                if (u.indexOf("//") === 0) {
                    u = "https:" + u;
                } else if (u.indexOf("http") !== 0) {
                    u = domain + (u.indexOf("/") === 0 ? "" : "/") + u;
                }
                if (!seen[u]) {
                    seen[u] = true;
                    urls.push('<img src="' + u + '">');
                }
            }
        }
    }

    // 3. 兜底提取常规全局 photos 图片链接
    if (urls.length === 0) {
        var mAll = str.match(/(?:https?:)?\\/\\/[^"'<>\\s]+(?:photos|media\\/photos)[^"'<>\\s]+\\.(?:jpg|png|webp|jpeg)/gi);
        if (mAll) {
            for (var k = 0; k < mAll.length; k++) {
                var rawLink = mAll[k];
                if (rawLink.indexOf("//") === 0) rawLink = "https:" + rawLink;
                if (!seen[rawLink]) {
                    seen[rawLink] = true;
                    urls.push('<img src="' + rawLink + '">');
                }
            }
        }
    }

    return urls.join('\\n');
})();
body = result;
result;
</js>"""

    # imageDecode - 混淆切片精准还原算法 (垂直条带倒序拼装)
    image_decode = """(function(result, src) {
    if (!result || result.length === 0) return result;
    if (src.indexOf("gif") !== -1 || src.indexOf("qyyuapi.com") !== -1) {
        return result;
    }

    // 匹配章节/本子ID与图片编号 (例如 /media/photos/268850/00001.webp)
    var mac = src.match(/photos\\/(\\d+)\\/(\\d+)/);
    if (!mac || !mac[1] || !mac[2]) {
        return result;
    }

    var bookId = Number(mac[1]);
    var imgId = mac[2];

    // 220980 之前的图片未进行切片乱序
    if (isNaN(bookId) || bookId < 220980) {
        return result;
    }

    // 计算切片分割条数 num
    var num = 10;
    if (bookId > 421925) {
        var md5 = java.md5Encode(bookId + "" + imgId);
        var ascii = md5.substr(-1).charCodeAt(0);
        num = (ascii % 8 + 1) * 2;
    } else if (bookId >= 268850) {
        var md5 = java.md5Encode(bookId + "" + imgId);
        var ascii = md5.substr(-1).charCodeAt(0);
        num = (ascii % 10 + 1) * 2;
    } else {
        num = 10;
    }

    var Magua = new JavaImporter();
    Magua.importPackage(Packages.java.io, Packages.android.graphics);
    with (Magua) {
        try {
            var img = BitmapFactory.decodeByteArray(result, 0, result.length);
            if (!img) return result;
            var height = img.getHeight();
            var width = img.getWidth();
            var y = Math.floor(height / num);
            var remainder = height % num;
            var newImg = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
            var canvas = new Canvas(newImg);
            for (var i = 1; i <= num; i++) {
                var h = (i === num) ? remainder : 0;
                var srcBlock = Bitmap.createBitmap(img, 0, y * (i - 1), width, y + h);
                canvas.drawBitmap(srcBlock, 0, height - y * i - h, null);
            }
            var newbit = new ByteArrayOutputStream();
            newImg.compress(Bitmap.CompressFormat.JPEG, 92, newbit);
            return newbit.toByteArray();
        } catch (e) {
            return result;
        }
    }
})(result, src);"""

    # 规范的完整 PC 端请求头，包含免弹窗验证 Cookie，完美模拟 PC 桌面 Chrome
    pc_header = json.dumps({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": "AVS=1; over18=1",
        "Referer": "https://18comic.vip/",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }, indent=2)

    source = {
        "bookSourceComment": "禁漫天堂官方直连书源（纯净免维护版）\n1. PC端标识：请求头原生采用桌面PC端User-Agent及完整Client Hints，默认注入AVS过审Cookie，杜绝弹窗阻断\n2. 纯净稳定：移除造成死循环误报的loginCheckJs，移除导致超时的无谓webJs轮询，秒级渲染列表\n3. 智能线路：支持在“源登录”界面一键打开发布页(jmcomic.me)，预设多组官方镜像线路，支持自定义域名输入与实时测速生效\n4. 深度评论：在作品详情页自动整合展示近期热评；并在目录中开辟专属「💬 读者讨论与精彩评论」章节，支持读者畅享完整书友讨论\n5. 切片还原：内置本地高保真切片解密算法（纯本地 BitmapFactory+Canvas 运算，无需依赖任何第三方外部服务器），毫秒级还原混淆漫画\n6. 极速缓冲：针对图片和网络加载慢特别调优 respondTime(180s) 与并发速率(2/1000)，有效防拉黑",
        "bookSourceGroup": "",
        "bookSourceName": "禁漫天堂",
        "bookSourceType": 2,
        "bookSourceUrl": "https://18comic.vip",
        "bookUrlPattern": "https?:\\/\\/(?:www\\.)?(?:18comic|jmcomic|jm-comic)\\w*\\.[a-z0-9]+\\/album\\/\\d+.*",
        "customButton": False,
        "customOrder": 1,
        "enabled": True,
        "enabledCookieJar": True,
        "enabledExplore": True,
        "header": pc_header,
        "jsLib": js_lib,
        "lastUpdateTime": 1792332000000,
        "loginUi": login_ui,
        "loginUrl": login_url,
        "respondTime": 180000,
        "concurrentRate": "2/1000",
        "weight": 0,
        "searchUrl": "/search/photos?search_query={{encodeURIComponent(key)}}&main_tag=0&page={{page}},{\"webView\":true}",
        "ruleSearch": {
            "checkKeyWord": "秘密",
            "bookList": ".row.m-0 > .list-col||.list-col||.thumb-overlay-albums",
            "name": ".video-title@text||.title-truncate@text||tag.a.0@title||a@title",
            "bookUrl": "a.0@href##$##,{\"webView\":true}",
            "coverUrl": "img@data-original||img@data-src||img@src##^/+##https://",
            "author": ".title-truncate.1@text||.author@text||.video-author@text",
            "kind": ".tag@text",
            "wordCount": "span.0@text##^##👍🏻",
            "intro": ".video-title@text"
        },
        "exploreUrl": explore_url,
        "ruleExplore": {
            "bookList": ".row.m-0 > .list-col||.list-col||.thumb-overlay-albums",
            "name": ".video-title@text||.title-truncate@text||tag.a.0@title||a@title",
            "bookUrl": "a.0@href##$##,{\"webView\":true}",
            "coverUrl": "img@data-original||img@data-src||img@src##^/+##https://",
            "author": ".title-truncate.1@text||.author@text||.video-author@text",
            "kind": ".tag@text",
            "wordCount": "span.0@text##^##👍🏻",
            "intro": ".video-title@text"
        },
        "ruleBookInfo": {
            "name": "h1#book-name@text||h1@text",
            "author": ".phone-author-tag@text||.tag-block:contains(作者) a@text||.tag-block:contains(標籤) a@text",
            "coverUrl": ".thumb-overlay img@data-original||.thumb-overlay img@src||#album-crop img@src##^/+##https://",
            "kind": "<js>java.getStringList('[data-type=tags] a@text||.tag-block a@text').toArray().join(',')</js>",
            "wordCount": ".train-number@text||.view-count@text",
            "updateTime": ".p-t-5.float-left@text##.*日期[：:]?\\s*",
            "tocUrl": "",
            "intro": intro_rule
        },
        "ruleToc": {
            "chapterList": toc_js,
            "chapterName": "title",
            "chapterUrl": "url"
        },
        "ruleContent": {
            "content": content_js,
            "imageStyle": "FULL",
            "imageDecode": image_decode
        }
    }

    return [source]

if __name__ == '__main__':
    data = build_book_source()
    output_path = 'book_sources/禁漫天堂.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Successfully generated {output_path}')
