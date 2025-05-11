const $ = selector => {
    return document.querySelector(selector);
};

const listElement = $(".list");
const allImagePaths = JSON.parse(listElement.dataset.imagePaths);


function findImageIndexBySrc(src) {
    const basePath = src.replace(/^https?:\/\/[^\/]+\//, '/');
    return allImagePaths.findIndex(path => basePath.endsWith(path.substring(path.indexOf('/static/'))));
}

function getNextImagePath() {
    const listItems = $(".list").querySelectorAll("li");
    if (listItems.length === 0) return allImagePaths[0];
    const lastAddedImgElement = listItems[listItems.length - 1].querySelector("img");
    if (!lastAddedImgElement) return allImagePaths[0];
    const lastAddedImgSrc = lastAddedImgElement.src;
    let lastAddedIndex = findImageIndexBySrc(lastAddedImgSrc);
    if (lastAddedIndex === -1) return allImagePaths[0];
    let nextIndex = (lastAddedIndex + 1) % allImagePaths.length;
    return allImagePaths[nextIndex];
}

function getPrevImagePath() {
    const listItems = $(".list").querySelectorAll("li");
    if (listItems.length === 0) return allImagePaths[allImagePaths.length - 1];
    let referenceImgElement = $(".prev img") || $(".act img") || $(".hide img");
    if (!referenceImgElement) return allImagePaths[allImagePaths.length - 1];
    const referenceImgSrc = referenceImgElement.src;
    let referenceIndex = findImageIndexBySrc(referenceImgSrc);
    if (referenceIndex === -1) return allImagePaths[allImagePaths.length - 1];
    let nextPrevIndex = (referenceIndex - 1 + allImagePaths.length) % allImagePaths.length;
    return allImagePaths[nextPrevIndex];
}

function next() {
    if ($(".hide")) {
        $(".hide").remove();
    }
    /* Step */
    if ($(".prev")) {
        $(".prev").classList.add("hide");
        $(".prev").classList.remove("prev");
    }
    if ($(".act")) {
        $(".act").classList.add("prev");
        $(".act").classList.remove("act");
    }
    if ($(".next")) {
        $(".next").classList.add("act");
        $(".next").classList.remove("next");
    }
    if ($(".new-next")) {
        $(".new-next").classList.remove("new-next");
    }
    const addedEl = document.createElement('li');
    const imgEl = document.createElement('img');
    imgEl.src = getNextImagePath();
    imgEl.alt = "Next Image";
    addedEl.appendChild(imgEl);
    $(".list").appendChild(addedEl);
    addedEl.classList.add("next", "new-next");
}

function prev() {
    if ($(".new-next")) {
        $(".new-next").remove();
    }
    /* Step */
    if ($(".next")) {
        $(".next").classList.add("new-next");
    }
    if ($(".act")) {
        $(".act").classList.add("next");
        $(".act").classList.remove("act");
    }
    if ($(".prev")) {
        $(".prev").classList.add("act");
        $(".prev").classList.remove("prev");
    }
    /* New Prev */
    if ($(".hide")) {
        $(".hide").classList.add("prev");
        $(".hide").classList.remove("hide");
    }
    const addedEl = document.createElement('li');
    const imgEl = document.createElement('img');
    imgEl.src = getPrevImagePath();
    imgEl.alt = "Previous Image";
    addedEl.appendChild(imgEl);
    $(".list").insertBefore(addedEl, $(".list").firstChild);
    addedEl.classList.add("hide");
}

const prevButton = document.querySelector('.carousel-control.prev');
const nextButton = document.querySelector('.carousel-control.next');

if (prevButton && nextButton) {
  prevButton.addEventListener('click', (event) => {
    event.preventDefault();
    prev();
  });

  nextButton.addEventListener('click', (event) => {
    event.preventDefault();
    next();
  });
}

slide = element => {
    if (element.tagName === 'IMG') {
        element = element.parentNode; // Get the LI
    }
    if (element.classList.contains('next')) {
        next();
    } else if (element.classList.contains('prev')) {
        prev();
    }
}
const slider = $(".list"),
    swipe = new Hammer($(".swipe"));
slider.onclick = event => {
    slide(event.target);
}
swipe.on("swipeleft", (ev) => {
    next();
});
swipe.on("swiperight", (ev) => {
    prev();
});