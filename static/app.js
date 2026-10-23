(() => {
  'use strict';
  const $ = (q, root=document) => root.querySelector(q);
  const $$ = (q, root=document) => [...root.querySelectorAll(q)];
  const escapeHtml = x => String(x??'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const root=$('#editor-root');
  const state={data:null, currentId:null, busy:false, tab:'overview',topic:'',topicIds:null};
  function toast(message,kind='ok'){
    let el=$('#toast');
    if(!el){el=document.createElement('div');el.id='toast';el.className='toast';el.setAttribute('role','status');document.body.appendChild(el)}
    el.textContent=message; el.dataset.kind=kind; el.classList.add('show');
    clearTimeout(toast._t); toast._t=setTimeout(()=>el.classList.remove('show'),6500);
  }
  async function api(path,body=null){
    let response=await fetch(path,{method:body===null?'GET':'POST',headers:{'Content-Type':'application/json','X-Signal-Request':'1'},credentials:'same-origin',body:body===null?undefined:JSON.stringify(body)});
    let data=await response.json().catch(()=>({error:'Invalid server response'}));
    if(!response.ok)throw Error(data.error||`Request failed (${response.status})`);
    return data;
  }
  async function subscription(form){
    const btn=$('button',form), feedback=$('.form-message',form), email=$('input[name="email"]',form).value.trim();
    btn.disabled=true; feedback.textContent='Requesting confirmation…';
    try {const result=await api('/api/subscribe',{email});feedback.textContent=result.message;form.reset()}
    catch(err){feedback.textContent=err.message}
    finally {btn.disabled=false}
  }
  $$('[data-subscribe-form]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();subscription(form)}));
  const search=$('#archive-search');
  if(search)search.addEventListener('input',()=>$$('.issue-card',$('#archive-grid')).forEach(c=>c.style.display=c.textContent.toLowerCase().includes(search.value.toLowerCase())?'':'none'));
  if(!root)return;

  function login(){
    root.innerHTML=`<section class="login-panel"><div class="eyebrow">PRIVATE / EDITOR ONLY</div><h2>Make something<br><em>worth sending.</em></h2><p>Enter your editor password to manage stories, AI drafts, approvals, and publication.</p><form id="login-form"><label for="admin-pass">Editor password</label><input id="admin-pass" type="password" autocomplete="current-password" placeholder="Your private password" required><button class="btn btn-dark" type="submit">Unlock workbench ↗</button></form></section>`;
    $('#login-form').addEventListener('submit',async e=>{
      e.preventDefault();const btn=$('button',e.target);btn.disabled=true;
      try{await api('/api/login',{password:$('#admin-pass').value});await refresh()}
      catch(err){toast(err.message,'error');btn.disabled=false}
    });
  }
  async function refresh(){
    try {state.data=await api('/api/admin/data');
      if(state.currentId&&!state.data.issues.some(x=>x.id===state.currentId))state.currentId=null;
      render();}
    catch(err){if(err.message.includes('Sign in'))login();else toast(err.message,'error')}
  }
  function tab(name,button){state.tab=name;state.currentId=null;render()}
  function shell(inner){
    const s=state.data.stats;
    root.innerHTML=`<div class="studio-top"><p>THE SIGNAL DAILY NEWSROOM <span>✳</span> POWERED BY ${escapeHtml(state.data.model)}</p><button id="logout" class="mini-link">Log out ↗</button></div>
    <div class="stats-grid"><div class="stat"><strong>${s.stories}</strong><span>NEWS SOURCES</span></div><div class="stat"><strong>${s.drafts}</strong><span>UNPUBLISHED</span></div><div class="stat"><strong>${s.published}</strong><span>PUBLISHED</span></div><div class="stat"><strong>${s.subscribers}</strong><span>SUBSCRIBERS</span></div></div>
    <div class="tabbar" role="tablist">${[['overview','Editions'],['sources','Source feed'],['import','Import local draft'],['settings','Publishing setup']].map(([v,label])=>`<button role="tab" aria-selected="${state.tab===v}" data-tab="${v}" class="${state.tab===v?'selected':''}">${label}</button>`).join('')}</div>
    <div class="studio-content">${inner}</div>`;
    $('#logout').addEventListener('click',async()=>{await api('/api/logout',{});state.data=null;login()});
    $$('[data-tab]').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab,b)));
  }
  function render(){
    if(state.currentId){editor();return}
    if(state.tab==='sources')return sourceTab();
    if(state.tab==='import')return importTab();
    if(state.tab==='settings')return settingsTab();
    const issues=state.data.issues;
    shell(`<div class="split-heading"><div><div class="eyebrow">ISSUES / EDITORIAL PIPELINE</div><h2>Your editions<span class="pink">.</span></h2></div><div class="action-stack"><button class="btn btn-outline" id="blank-draft">+ New blank edition</button><button class="btn btn-dark" id="quick-generate">✳ Generate with Gemma</button></div></div>
     <div class="notice"><strong>Approval gate is enabled.</strong> A Gemma draft cannot publish until you review and approve it. ${state.data.mailer?'Verified subscribers receive the approved issue on publication.':'Email is disabled. Publishing makes an approved edition readable on this server; no subscriber emails will be sent.'}</div>
    ${issues.length?`<div class="issues-table">${issues.map(i=>`<button class="edition-row" data-open="${i.id}"><span class="status-tag status-${i.status}">${i.status.toUpperCase()}</span><span class="edition-title">${escapeHtml(i.title)}<small>${escapeHtml((i.updated_at||'').slice(0,10))} · ${i.items.length} stories</small></span><span class="row-arrow">↗</span></button>`).join('')}</div>`:
     `<div class="empty-state"><span class="empty-symbol">✳</span><h3>No editions yet.</h3><p>Collect sources and generate your first local-AI draft, or start manually.</p></div>`}`);
    $('#blank-draft').addEventListener('click',async()=>{
      await action(async()=>{const x=await api('/api/admin/manual',{title:'Untitled AI briefing',subject:'Untitled AI briefing',intro:'',closing:'',items:[]});await refresh();state.currentId=x.issue_id;editor()})
    });
    $('#quick-generate').addEventListener('click',()=>action(async()=>{
      toast('Asking your local Gemma model to prepare a grounded draft.');
      const x=await api('/api/admin/draft',{});await refresh();state.currentId=x.issue_id;editor();toast('Gemma draft created. Review each claim before approval.');
    }));
    $$('[data-open]').forEach(b=>b.addEventListener('click',()=>{state.currentId=Number(b.dataset.open);editor()}));
  }
  async function action(fn){
    if(state.busy)return;
    state.busy=true;
    $$('button').forEach(b=>{if(b.id!=='logout')b.disabled=true});
    try{await fn()}catch(err){toast(err.message,'error')}finally{state.busy=false;$$('button').forEach(b=>b.disabled=b.dataset.dirtyDisabled==='1')}
  }
  function itemMarkup(item={},idx=0){
    return `<fieldset class="story-form" data-original-url="${escapeHtml(item.url||'')}" data-source-title="${escapeHtml(item.source_title||'')}" data-source-description="${escapeHtml(item.source_description||'')}" data-published-at="${escapeHtml(item.published_at||'')}"><legend>STORY ${idx+1}${state.data?.issues.find(x=>x.id===state.currentId)?.status==='published'?'':'<button type="button" class="remove-story mini-link">Remove ×</button>'}</legend>
     <div class="form-field"><label>Headline</label><input name="headline" value="${escapeHtml(item.headline||'')}" required></div>
     <div class="form-field"><label>Summary (fact-checked)</label><textarea name="summary" rows="3" required>${escapeHtml(item.summary||'')}</textarea></div>
     <div class="form-field"><label>Why it matters</label><textarea name="why" rows="2">${escapeHtml(item.why||'')}</textarea></div>
     <div class="two-fields"><div class="form-field"><label>Source name</label><input name="source" value="${escapeHtml(item.source||'Original source')}"></div><div class="form-field"><label>Source URL</label><input name="url" type="url" value="${escapeHtml(item.url||'')}" required placeholder="https://…"></div></div>
    </fieldset>`;
  }
  function editor(){
    const issue=state.data.issues.find(i=>i.id===state.currentId);
    if(!issue){state.currentId=null;render();return}
    state.tab='overview';
    const isPublished=issue.status==='published';
    shell(`<button class="back-button" id="back-to-issues">← Back to all editions</button><div class="editor-header"><div><div class="eyebrow">EDITION #${issue.id} / ${issue.status.toUpperCase()}</div><h2>${escapeHtml(issue.title)}<span class="pink">.</span></h2></div><span class="status-tag status-${issue.status}">${issue.status.toUpperCase()}</span></div>
    <form id="issue-form" class="issue-form"><div class="two-fields"><div class="form-field"><label>Issue title</label><input name="title" value="${escapeHtml(issue.title)}" maxlength="180" required ${isPublished?'disabled':''}></div><div class="form-field"><label>Email subject</label><input name="subject" value="${escapeHtml(issue.subject)}" required ${isPublished?'disabled':''}></div></div>
     <div class="form-field"><label for="issue-topic">Topic</label><select id="issue-topic" name="topic" ${isPublished?'disabled':''}>${['AI','Research','Tools','Industry'].map(t=>`<option ${issue.topic===t?'selected':''}>${t}</option>`).join('')}</select></div><div class="form-field"><label>Opening / editorial introduction</label><textarea name="intro" rows="3" ${isPublished?'disabled':''}>${escapeHtml(issue.intro)}</textarea></div>
     <div class="section-label">THE STORIES <span>Fact-check each link and claim before approving.</span></div><div id="story-fields">${issue.items.map(itemMarkup).join('')}</div>
     ${!isPublished?'<button type="button" class="btn btn-outline" id="add-story">+ Add another story</button>':''}
     <div class="form-field closing-field"><label>Closing note</label><textarea name="closing" rows="3" ${isPublished?'disabled':''}>${escapeHtml(issue.closing)}</textarea></div>
     <div class="editor-actions">${!isPublished?`<button type="submit" class="btn btn-outline">Save as draft</button>${issue.status==='draft'?'<button type="button" class="btn btn-dark" id="review-issue">Submit for review →</button>':''}${issue.status==='review'?'<button type="button" class="btn btn-dark" id="approve-issue">✓ Approve reviewed edition</button>':''}${['review','approved'].includes(issue.status)?'<button type="button" class="btn btn-outline" id="revise-issue">Request revision</button>':''}${issue.status==='approved'?`<button type="button" class="btn btn-accent" id="publish-issue">${state.data.mailer?'Publish + notify subscribers':'Publish online only'} ↗</button>`:''}`:
     `<a href="/issue/${encodeURIComponent(issue.slug)}" target="_blank" rel="noopener" class="btn btn-outline">View published edition ↗</a>${state.data.mailer?'<button type="button" class="btn btn-dark" id="retry-send">Send / retry subscriber delivery ↗</button>':'<p class="muted">Email is disabled. No subscriber delivery is available.</p>'}`}</div></form>`);
    $('#back-to-issues').addEventListener('click',()=>{state.currentId=null;state.tab='overview';render()});
    if(!isPublished){
      $('#add-story').addEventListener('click',()=>{$('#story-fields').insertAdjacentHTML('beforeend',itemMarkup({},$$('.story-form').length));wireRemoves();form.dispatchEvent(new Event('input',{bubbles:true}))});
      $('#issue-form').addEventListener('submit',e=>{e.preventDefault();action(async()=>{await api(`/api/admin/issue/${issue.id}/save`,{...gather(),version:issue.version});toast('Draft saved. Approval reset so you can review changes.');await refresh()})});
      const review=$('#review-issue');if(review)review.addEventListener('click',()=>action(async()=>{await api(`/api/admin/issue/${issue.id}/save`,{...gather(),version:issue.version});await api(`/api/admin/issue/${issue.id}/review`,{});toast('Submitted for review. Preview and fact-check before approval.');await refresh()}));
      const revise=$('#revise-issue');if(revise)revise.addEventListener('click',()=>action(async()=>{await api(`/api/admin/issue/${issue.id}/revise`,{});await refresh()}));
      const approve=$('#approve-issue'); if(approve)approve.addEventListener('click',()=>action(async()=>{await api(`/api/admin/issue/${issue.id}/approve`,{version:issue.version});toast('Edition approved. Review completed; you can publish now.');await refresh()}));
      const pub=$('#publish-issue');if(pub)pub.addEventListener('click',()=>{
        if(!confirm(state.data.mailer?'Publish this approved edition to your website and email verified subscribers?':'Publish this approved edition on this server? Email is disabled; no messages will be sent.'))return;
        action(async()=>{const result=await api(`/api/admin/issue/${issue.id}/publish`,{version:issue.version});toast(`Published! Emails sent: ${result.sent}, failed: ${result.failed}. ${result.note}`);await refresh()})
      });
    } else if($('#retry-send')) $('#retry-send').addEventListener('click',()=>action(async()=>{const r=await api(`/api/admin/issue/${issue.id}/send`,{});toast(`Delivery: ${r.sent} sent, ${r.failed} failed, ${r.remaining} remaining.`)}));
    // Approval always applies to the saved revision, never to unsaved visible edits.
    const form=$('#issue-form');
    if(isPublished)$$('input,textarea,select',form).forEach(el=>el.disabled=true);
    if(!isPublished)form.addEventListener('input',()=>{['approve-issue','publish-issue'].forEach(id=>{const button=$('#'+id);if(button){button.disabled=true;button.dataset.dirtyDisabled='1';button.title='Save changes and submit for review again'}})});
    const preview=document.createElement('details');preview.className='draft-preview';
    preview.innerHTML=`<summary>Preview saved edition</summary><article><h2>${escapeHtml(issue.title)}</h2><p>${escapeHtml(issue.intro)}</p>${issue.items.map(i=>`<section><h3>${escapeHtml(i.headline)}</h3><p>${escapeHtml(i.summary)}</p><p><strong>Why it matters:</strong> ${escapeHtml(i.why)}</p><a href="${escapeHtml(i.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(i.source)}</a>${i.source_description?`<details><summary>Collected source evidence</summary><p>${escapeHtml(i.source_description)}</p></details>`:''}</section>`).join('')}<p>${escapeHtml(issue.closing)}</p></article>`;
    form.after(preview);
    const history=document.createElement('details');history.innerHTML='<summary>Edition history</summary><p>Loading…</p>';preview.after(history);
    api(`/api/admin/issue/${issue.id}/history`).then(r=>{history.innerHTML='<summary>Edition history</summary><ol>'+r.events.map(e=>`<li>${escapeHtml(e.action)} · ${escapeHtml(e.created_at)}</li>`).join('')+'</ol>'}).catch(err=>{history.textContent=err.message});
    $$('input,textarea,select',root).forEach((el,i)=>{if(!el.id||el.id.startsWith('editor-field-'))el.id='editor-field-'+i;const label=el.parentElement.querySelector('label');if(label&&!label.htmlFor)label.htmlFor=el.id});
    wireRemoves();
    function wireRemoves(){ $$('input,textarea,select',root).forEach((el,i)=>{if(!el.id||el.id.startsWith('editor-field-'))el.id='editor-field-'+i;const label=el.parentElement.querySelector('label');if(label)label.htmlFor=el.id}); $$('.remove-story').forEach(b=>{b.onclick=()=>{b.closest('.story-form').remove();form.dispatchEvent(new Event('input',{bubbles:true}));$$('.story-form legend').forEach((leg,i)=>{leg.firstChild.textContent='STORY '+(i+1)})}}) }
  }
  function gather(){
    const form=$('#issue-form');
    const field=n=>form.querySelector(`[name="${n}"]`).value;
    return {topic:field('topic'),title:field('title'),subject:field('subject'),intro:field('intro'),closing:field('closing'),items:$$('.story-form').map(el=>{
      const v=name=>el.querySelector(`[name="${name}"]`).value;
      return {headline:v('headline'),summary:v('summary'),why:v('why'),source:v('source'),url:v('url'),source_title:v('url')===el.dataset.originalUrl?el.dataset.sourceTitle||'':'',source_description:v('url')===el.dataset.originalUrl?el.dataset.sourceDescription||'':'',published_at:v('url')===el.dataset.originalUrl?el.dataset.publishedAt||'':''};
    })};
  }
  function sourceTab(){
    const stories=state.topicIds===null?state.data.stories:state.topicIds.map(id=>state.data.stories.find(s=>s.id===id)).filter(Boolean);
    shell(`<div class="split-heading"><div><div class="eyebrow">INGESTION / PRIMARY SOURCES</div><h2>The source feed<span class="pink">.</span></h2><p class="muted">Fetches RSS/Atom feeds. Drafts are written from feed summaries with source links.</p></div><button class="btn btn-dark" id="fetch-news">↓ Refresh news sources</button></div>
     <div class="form-field"><label for="source-topic">Newsletter topic</label><input id="source-topic" maxlength="200" placeholder="Latest developments in open-source AI models" value="${escapeHtml(state.topic)}"><p>Searches configured trusted RSS feeds only. Select the final sources below; insufficient sources never create invented news.</p></div>${state.topicIds!==null?`<p role="status">${stories.length} relevant current cached stories found. Review the source dates before selecting.</p>`:''}${stories.length?`<div class="source-toolbar"><span>${stories.length} stories cached</span><button class="btn btn-accent" id="make-selected">Generate selected with Gemma ↗</button></div><div class="source-list">${stories.map(s=>`<label class="source-row"><input type="checkbox" name="story" value="${s.id}"><span class="source-details"><b>${escapeHtml(s.title)}</b><small>${escapeHtml(s.source)} · ${escapeHtml((s.published_at||s.created_at).slice(0,10))}</small><span class="source-description">${escapeHtml(s.description)}</span><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">Original story ↗</a></span></label>`).join('')}</div>`:
     `<div class="empty-state"><h3>Your source feed is empty.</h3><p>Click refresh to fetch available stories from configured sources.</p></div>`}`);
    $('#fetch-news').addEventListener('click',()=>action(async()=>{state.topic=$('#source-topic').value.trim();const data=await api('/api/admin/ingest',{topic:state.topic});state.topicIds=state.topic?data.matching_ids:null;toast(`${data.added} new stories imported.${data.errors.length?' Some sources failed: '+data.errors.join(' | '):''}`,data.errors.length?'warning':'ok');await refresh()}));
    const selected=$('#make-selected');if(selected)selected.addEventListener('click',()=>action(async()=>{
      const ids=$$('input[name="story"]:checked').map(x=>Number(x.value));
      if(!ids.length||ids.length>8)throw Error('Select between 1 and 8 stories');
      toast('Generating a local Gemma draft from your selected sources.');
      const x=await api('/api/admin/draft',{story_ids:ids,topic:state.topic});await refresh();state.currentId=x.issue_id;editor();toast('Draft ready. Verify all details and approve before publishing.');
    }));
  }
  function importTab(){
    shell(`<div class="eyebrow">LOCAL / OFFLINE GENERATION</div><h2>Bring your draft<span class="pink">.</span></h2>
      <p class="settings-lead">If your public site runs on a remote server, keep Ollama private on your laptop. Run <code>python tools/local_generate.py</code> on your laptop and import the generated JSON here.</p>
      <form id="import-form"><div class="form-field"><label for="json-import">Paste newsletter JSON (or upload a .json file)</label><textarea id="json-import" rows="12" placeholder='{"title":"...","subject":"...","intro":"...","closing":"...","items":[{"headline":"...","summary":"...","why":"...","source":"...","url":"https://..."}]}' required></textarea></div><label for="import-file">Upload newsletter JSON</label><input type="file" accept=".json,application/json" id="import-file"><button class="btn btn-dark" type="submit">Import as unapproved draft ↗</button></form>`);
    $('#import-file').addEventListener('change',async e=>{if(e.target.files[0])$('#json-import').value=await e.target.files[0].text()});
    $('#import-form').addEventListener('submit',e=>{e.preventDefault();action(async()=>{
      let data;try{data=JSON.parse($('#json-import').value)}catch{throw Error('Enter valid JSON')}
      const x=await api('/api/admin/import',data);await refresh();state.currentId=x.issue_id;editor();toast('Imported. Review and approve before publishing.');
    })});
  }
  function settingsTab(){
    shell(`<div class="eyebrow">CONFIG / DELIVERY</div><h2>Publishing setup<span class="pink">.</span></h2>
    <p class="settings-lead">Model generation stays on your computer. Public subscriptions require working SMTP credentials and an HTTPS public URL.</p>
    <div class="settings-grid"><div class="settings-item"><small>GEMMA MODEL</small><h3>${escapeHtml(state.data.model)}</h3><p>Configured with <code>OLLAMA_MODEL</code>. Your installed model tag may differ.</p></div><div class="settings-item"><small>EMAIL STATUS</small><h3>${state.data.mailer?'SMTP configured':'SMTP missing'}</h3><p>${state.data.mailer?'Delivery is enabled. Test using an email address you own before inviting subscribers.':'Set SMTP_HOST, MAIL_FROM, and credentials on the host to enable subscriptions.'}</p></div><div class="settings-item"><small>APPROVAL MODE</small><h3>Human-in-the-loop</h3><p>All new editions start as drafts. Review → Approve → Publish. Edits reset approval.</p></div><div class="settings-item"><small>PRODUCTION HOSTING</small><h3>Persistent Python host</h3><p>A VPS/container with a persistent SQLite volume is supported. Pure serverless hosting is not recommended for this build.</p></div></div>
    <div class="notice">Deployment checklist: HTTPS URL, secure admin password, SMTP, verified sender/DKIM/SPF, persistent storage, backups, and a live test subscription.</div>`);
  }
  (async()=>{
    try{const s=await api('/api/admin/status');if(s.authenticated)await refresh();else login()}
    catch(err){root.textContent='Cannot contact backend: '+err.message}
  })();
})();
