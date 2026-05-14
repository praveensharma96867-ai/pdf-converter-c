const toggle = document.getElementById("themeToggle");

if(toggle){

toggle.addEventListener("change",()=>{

document.body.classList.toggle("dark");

});

}

const dropArea = document.getElementById("dropArea");

if(dropArea){

dropArea.addEventListener("dragover",(e)=>{
e.preventDefault();
dropArea.style.background="#e0e7ff";
});

dropArea.addEventListener("dragleave",()=>{
dropArea.style.background="";
});

dropArea.addEventListener("drop",(e)=>{

e.preventDefault();

const fileInput = dropArea.querySelector("input");

fileInput.files = e.dataTransfer.files;

dropArea.style.background="";

});

}