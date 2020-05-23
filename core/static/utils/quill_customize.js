
const qlToolbar = document.querySelector('.ql-toolbar');
const sticky = qlToolbar.offsetTop;
window.onscroll = function() { fixToolbar()};
function fixToolbar(){
  const pageOffest = window.pageYOffset
  if( pageOffest > sticky){
      qlToolbar.classList.add("sticky-toolbar");
  }
  else{
    qlToolbar.classList.remove("sticky-toolbar");
  }
}
