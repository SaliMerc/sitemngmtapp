const new_site=document.getElementById("site_name_new")
const existing_site=document.getElementById("site_name_exist")
const site_type=document.getElementById("site_type")
site_type.addEventListener('change', function (){
    if (this.value==='new_site'){
        new_site.style.display='block'
        existing_site.style.display='none'
    }
    else if (this.value==='existing_site'){
        new_site.style.display='none'
        existing_site.style.display='block'
    }
    else{
        new_site.style.display='none'
        existing_site.style.display='none'
    }
})

// const burger=document.getElementsByClassName("burger")
// const close=document.getElementsByClassName("close")
// const nav_list=document.getElementsByClassName("nav-lists")
// burger.addEventListener('click',function (){
//     burger.style.display='none';
//     close.style.display='block';
//     nav_list.style.display="block";
//     nav_list.style.display="flex";
//     nav_list.style.flexDirection="column";
// })
// close.addEventListener('click',function (){
//     burger.style.display='block';
//     close.style.display='none';
//     nav_list.style.display='none';
// })