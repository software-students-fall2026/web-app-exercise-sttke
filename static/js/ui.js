var LETTERS="ABCDEFGHIJKLNOPQRSTUVXYZ";
var PLAYED_KEY = "wordmark-decoded";


function letterWidths(el) 
{
  var probe=document.createElement("span");

  probe.style.position="absolute";
  probe.style.visibility="hidden";

  el.appendChild(probe);

  var widths={};

  for (var i =0; i<LETTERS.length;i++) 
  {



    probe.textContent=LETTERS[i];

    widths[LETTERS[i]]=probe.getBoundingClientRect().width;
  }

  el.removeChild(probe);
  return widths;
}




function lettersThatFit(letter,slotWidth,widths) 
{
  var fit=[];

  for (var i = 0; i<LETTERS.length;i++) 
  {

    if (widths[LETTERS[i]]<=slotWidth+0.5) 
    {


      fit.push(LETTERS[i]);
    }

  }


  if (fit.length===0) 
  {
    fit.push(letter);
  }


  return fit;
}


function scramble(el) 
{
  var text=el.textContent;
  var spans=[];

  el.textContent="";

  for (var i = 0;i<text.length;i++) 
  {
    var span=document.createElement("span");
    span.textContent = text[i];
    el.appendChild(span);
    spans.push(span);
  }


  var widths=letterWidths(el);
  var pools=[];
  for (var i = 0; i<spans.length; i++) 
  {
    var w=spans[i].getBoundingClientRect().width;
    spans[i].style.width =w+"px";
    pools.push(lettersThatFit(text[i], w, widths));
  }


  var start=null;

  function frame(now) 
  {
    if (start===null) 
    {
      
      start = now;
    }


    var t=Math.min((now-start)/900,1);
    var settled = Math.floor(t*text.length);

    for (var i = 0; i<spans.length;i++) 
    {

      if (i<settled) 
      {
        spans[i].textContent=text[i];
        spans[i].classList.remove("is-scrambled");
      }


      else 
      {
        var pool=pools[i];
        spans[i].textContent =pool[Math.floor(Math.random()*pool.length)];
        spans[i].classList.add("is-scrambled");
      }

    }


    if (t<1) 
    {
      requestAnimationFrame(frame);
    }

  }
  requestAnimationFrame(frame);
}


function startWordmark() 
{

  if (sessionStorage.getItem(PLAYED_KEY)==="1") 
    {
      return;
    }

  sessionStorage.setItem(PLAYED_KEY,"1");

  document.fonts.ready.then(function () 
  {
    var marks =document.querySelectorAll(".wordmark");

    for (var i = 0; i<marks.length; i++) 
    {
      scramble(marks[i]);
    }

  });
}


function easeOut(t) 
{
  return 1-Math.pow(1-t, 3);
}


function countUp(el) 
{
  if (el.hasAttribute("data-counted")) {return;}


  el.setAttribute("data-counted", "");

  var end=parseInt(el.getAttribute("data-count"),10);

  if (isNaN(end) || end<=0) {return;}

  var finalText=el.textContent;

  el.style.display="inline-block";
  el.style.minWidth =el.getBoundingClientRect().width+"px";
  el.textContent="0";
  var start=null;


  function frame(now) 
  {
    if (start===null) 
    {
      start=now;
    }

    var t=Math.min((now-start) /900,1);


    if (t<1) 
    {
      el.textContent=Math.round(end*easeOut(t));
      requestAnimationFrame(frame);
    }

    else 
    {
      el.textContent=finalText;
    }
  }

  requestAnimationFrame(frame);
}


function startCounters() 
{
  var watcher=new IntersectionObserver(function (entries) 
  {

    for (var i =0; i<entries.length;i++) 
    {

      if (entries[i].isIntersecting) 
      {
        watcher.unobserve(entries[i].target);
        countUp(entries[i].target);
      }

    }
  }, { threshold: 0.5 });


  var counters=document.querySelectorAll("[data-count]");

  for (var i =0;i<counters.length;i++) 
  {

    if (counters[i].getBoundingClientRect().top<window.innerHeight) 
    {
      countUp(counters[i]);
    }

    else 
    {
      watcher.observe(counters[i]);
    }
  }
}


function cardOf(target) 
{
  return target.closest(".card");
}


function lightCard(card, e) 
{
  var box=card.getBoundingClientRect();

  var x =(e.clientX-box.left)/box.width*100;
  var y = (e.clientY-box.top)/box.height*100;


  card.style.background="radial-gradient(220px 220px at " +x.toFixed(1) + "% " + y.toFixed(1) + "%, #FFFFFF, #FBF8F1 70%)";
}




function startCards() 
{
  document.addEventListener("pointermove",function (e) 
  {

    if (e.pointerType !== "mouse") 
      {
        return;
      }


    var card=cardOf(e.target);

    if (card) 
    {
      lightCard(card,e);
    }

  });

  document.addEventListener("pointerout", function (e) 
  {
    if (e.pointerType!=="mouse") {
      return;
    }
    var card=cardOf(e.target);

    if (card && !card.contains(e.relatedTarget)) 
    {
      card.style.background="";
    }
  });

  document.addEventListener("pointerdown", function (e) 
  {
    var card=cardOf(e.target);
    if (!card) {return;}

    lightCard(card,e);

    if (e.pointerType==="mouse") {return;}

    setTimeout(function () 
    {
      card.style.background="";
    }, 600);

  });
}


if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) 
{
  startCounters();
  startCards();
  startWordmark();
}