// Vercel serverless endpoint: admin key is never exposed in client code.
export default async function handler(req,res) {
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'POST only'});
  const { ADMIN_UPDATE_KEY, GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_BRANCH='main' }=process.env;
  if(!ADMIN_UPDATE_KEY || !GITHUB_TOKEN || !GITHUB_REPOSITORY) return res.status(503).json({error:'Server environment variables are not configured'});
  const key=req.headers['x-admin-key'];
  const crypto=await import('node:crypto');
  const a=Buffer.from(String(key||'')),b=Buffer.from(ADMIN_UPDATE_KEY);
  if(a.length!==b.length || !crypto.timingSafeEqual(a,b)) return res.status(401).json({error:'관리자 인증 실패'});
  try {
    const url=`https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/sync.yml/dispatches`;
    const response=await fetch(url,{method:'POST',headers:{Authorization:`Bearer ${GITHUB_TOKEN}`,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'},body:JSON.stringify({ref:GITHUB_BRANCH})});
    if(response.status!==204) return res.status(502).json({error:`GitHub workflow dispatch failed (${response.status})`});
    return res.status(202).json({message:'업데이트 작업을 시작했습니다. GitHub Actions 완료 후 사이트를 새로고침하세요.'});
  } catch(e) {return res.status(502).json({error:'GitHub 연결 실패'});}
}
