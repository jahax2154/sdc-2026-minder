const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright'),assert=require('assert'),fs=require('fs');
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106';
const output=process.env.MINDER_BROWSER_OUTPUT_DIR||'/private/tmp/minder-f-ux';fs.mkdirSync(output,{recursive:true});
async function api(page,endpoint,body,method=body===undefined?'GET':'POST'){return page.evaluate(async({endpoint,body,method})=>{const r=await fetch('/api/'+endpoint,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});const data=await r.json();if(!r.ok)throw new Error(endpoint+' '+r.status);return data;},{endpoint,body,method});}
module.exports={chromium,assert,fs,api,base,output};
