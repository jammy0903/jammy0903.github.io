---
layout: post
title: "GitHub API로 정적 블로그에 글쓰기 버튼 달기"
subtitle: "Jekyll + GitHub Pages에서 브라우저만으로 포스팅하는 법"
date: 2026-03-08 12:00:00 +0900
categories: blog
tags: ['github', 'jekyll', 'javascript', 'api']
---

GitHub Pages로 블로그를 운영하다 보면 항상 불편한 점이 하나 있다.

> "글 하나 쓰려면 VSCode 켜고, 파일 만들고, front matter 작성하고, git commit, push..."

매번 이 과정을 거쳐야 한다. 마크다운 에디터 하나만 있으면 될 것 같은데.

그래서 만들었다. **브라우저에서 바로 글을 쓰고 발행하는 페이지.**

---

## 핵심 아이디어

GitHub에는 [Contents API](https://docs.github.com/en/rest/repos/contents)가 있다.

```
PUT /repos/{owner}/{repo}/contents/{path}
```

이 API에 파일 경로와 Base64로 인코딩한 내용을 보내면, GitHub이 직접 해당 파일을 레포에 커밋해준다. 즉, git 없이 파일을 만들 수 있다.

Jekyll 블로그의 포스트는 `_posts/2026-03-08-제목.md` 형태의 파일이니까, 이 API로 직접 만들면 GitHub Actions가 자동으로 빌드해서 블로그에 올라간다.

---

## 흐름

```
사용자 → 브라우저 에디터 → GitHub Contents API → _posts/ 에 파일 생성
                                                 → GitHub Actions 빌드
                                                 → GitHub Pages 배포
```

서버 없음. 백엔드 없음. 순수 클라이언트 JavaScript만으로 동작한다.

---

## 구현 핵심 코드

### 1. 마크다운 → Front Matter 조립

```javascript
function buildFrontMatter(title, date, tags) {
  return `---
layout: post
title: "${title}"
date: ${date} 12:00:00 +0900
categories: blog
tags: [${tags.map(t => `'${t}'`).join(', ')}]
---

`;
}
```

### 2. UTF-8 → Base64 (한글 포함 안전 처리)

한글이 포함된 경우 `btoa()`를 그냥 쓰면 에러가 난다.

```javascript
const encoded = btoa(unescape(encodeURIComponent(fullText)));
```

`encodeURIComponent` → `unescape` → `btoa` 순서로 처리하면 한글도 문제없다.

### 3. GitHub API 호출

```javascript
const res = await fetch(
  `https://api.github.com/repos/${OWNER}/${REPO}/contents/_posts/${filename}`,
  {
    method: 'PUT',
    headers: {
      'Authorization': `token ${githubToken}`,
      'Accept': 'application/vnd.github+json',
    },
    body: JSON.stringify({
      message: `Add post: ${title}`,
      content: encoded,
      branch: 'main',
    }),
  }
);
```

응답이 `201 Created`면 성공. 파일이 레포에 생기고, 1~2분 후 블로그에 반영된다.

---

## 에디터는 EasyMDE

[EasyMDE](https://github.com/Ionaru/easy-markdown-editor)를 CDN으로 붙였다.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.css">
<script src="https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.js"></script>

<textarea id="editor"></textarea>
<script>
const editor = new EasyMDE({ element: document.getElementById('editor') });
</script>
```

툴바, 미리보기, 전체화면, 자동저장까지 딸려온다. 설치도 필요 없다.

---

## 결과

이제 블로그에 `/write` 경로로 접속하면 마크다운 에디터가 뜨고, 작성 후 버튼 하나로 발행된다.

터미널 안 켜도 된다. VSCode 안 켜도 된다. 심지어 휴대폰 브라우저에서도 글을 쓸 수 있다.

정적 사이트라서 불가능할 것 같았는데, GitHub API 덕분에 생각보다 훨씬 깔끔하게 됐다.

---

*이 글은 Claude가 직접 작성하고 GitHub API로 발행했습니다.*
