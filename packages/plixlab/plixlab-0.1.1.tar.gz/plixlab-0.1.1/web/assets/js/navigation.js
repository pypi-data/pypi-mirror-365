import { toggleAnimations } from './models.js';

window.addEventListener('load', async function() {


document.addEventListener('keydown', function(event) {
   
    if (window.dataStore.mode == 'presentation') {
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
            incrementSlide();
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
            decrementSlide() ;
        }
    }

    if (window.dataStore.mode == 'full') {
     if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
        incrementEvent();
     } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
        decrementEvent() ;
     }
    }

  })


document.getElementById('aleft').addEventListener('click', function(event) {
    if (window.dataStore.mode == 'presentation') {
        decrementSlide();
    }
});

document.getElementById('aright').addEventListener('click', function(event) {
    if (window.dataStore.mode == 'presentation') {
        incrementSlide();
    }
}); 




function incrementEvent() {    


   const totalSlides = document.querySelectorAll(".slide").length;
   //const NSlideEvents = window.dataStore.animation['S' + String(window.dataStore.active_slide)].length
   //const NSlideEvents = window.dataStore.presentation.slides['S' + String(window.dataStore.active_slide)].animation.length


   const slide_ids = Object.keys(window.dataStore.presentation.slides)
   const NSlideEvents = window.dataStore.presentation.slides[slide_ids[window.dataStore.active_slide]].animation.length


   if (window.dataStore.index < NSlideEvents - 1){
      window.dataStore.index += 1; 
    } else { incrementSlide()}
      
    updateEventVisibility()
}


function decrementEvent() {    


   if (window.dataStore.index > 0){
      window.dataStore.index -= 1;    
   } else { decrementSlide()}

    updateEventVisibility()

}


function change_plotly_static(slide,staticc){

    
   // const slideElement = document.getElementById(slide);

   
   // const plotlyElements = slideElement.querySelectorAll('.PLOTLY');

   // plotlyElements.forEach(element => {
        
   //     Plotly.react(element.id, element.data, element.layout, {staticPlot: staticc,responsive: true,scrollZoom: true} );   
       

   // });

}


function decrementSlide() {
    if (window.dataStore.active_slide > 0) {
        window.dataStore.active_slide -= 1;



        const slide_ids = Object.keys(window.dataStore.presentation.slides)
        window.dataStore.index = window.dataStore.presentation.slides[slide_ids[window.dataStore.active_slide]].animation.length -1
        const old_slide_id = slide_ids[window.dataStore.active_slide+1]
        const new_slide_id = slide_ids[window.dataStore.active_slide]


        document.getElementById(old_slide_id).style.visibility = 'hidden'

        const slide =  document.getElementById(new_slide_id)
        slide.style.visibility = 'visible'

        //if (!slide.hasAttribute('tabindex')) {
        //    slide.setAttribute('tabindex', '-1');
       // }
       // slide.focus()

        change_plotly_static(old_slide_id,true)
       /change_plotly_static(new_slide_id,false)

   //     updateURL()
      
    }

}



function incrementSlide() {
    const totalSlides = document.querySelectorAll(".slide").length;
     if (window.dataStore.active_slide < totalSlides - 1) {
        window.dataStore.active_slide += 1
        window.dataStore.index = 0


        const slide_ids = Object.keys(window.dataStore.presentation.slides)
        
        const old_slide_id = slide_ids[window.dataStore.active_slide-1]
        const new_slide_id = slide_ids[window.dataStore.active_slide]



        document.getElementById(old_slide_id).style.visibility = 'hidden'

        const slide = document.getElementById(new_slide_id)
        slide.style.visibility = 'visible'


        change_plotly_static(old_slide_id,true)
        change_plotly_static(new_slide_id,false)

       // updateURL()

    }
}
   

//function updateURL() {
//    let currentUrl = window.location.href;
    
    // Use a regex to detect and remove the pattern #N followed by numbers
//    const hashPattern = /#\d+$/;
//    if (hashPattern.test(currentUrl)) {
//        currentUrl = currentUrl.replace(hashPattern, '');
//    }
    
    // Append the new hash fragment.
//    currentUrl += "#" + String(window.dataStore.active_slide);
    
 //   window.history.replaceState(null, null, currentUrl);
//}



function updateEventVisibility() {
    //SLIDEs use visible/hidden
    //Elements use visible/inherit
   

    const slide_id = Object.keys(window.dataStore.presentation.slides)[window.dataStore.active_slide]
    const arr = window.dataStore.presentation.slides[slide_id].animation[window.dataStore.index];

    for (let key in arr) {
        let element = document.getElementById(slide_id + '_' + key);
        

        if (arr[key]) {
            element.style.visibility = 'hidden';
            
            if (element.className === 'PLOTLY'){
                 element.hidden=true
            }
        } else {
            element.style.visibility = 'inherit';
            if (element.className === 'PLOTLY'){
                element.hidden=false
           }
        }
    } 
}




function updatePlotly(){

    //TODO: We need to avoid rerendering this. 
    const containers = document.querySelectorAll('.plotly');

    // Loop through each container
    containers.forEach(container => {
    if (window.dataStore.mode === 'grid') {
      container.hidden = true;
   } else {
     container.hidden = false;
   }
   });
}


document.body.addEventListener('click', e => {
    
    if (e.target.classList.contains('slide')) {

        if (window.dataStore.mode === 'grid'){

        const clickedSlideIndex = e.target.id;
        const slides_ids = Object.keys(window.dataStore.presentation.slides)
        
      
        const old_active_slide = window.dataStore.active_slide
        
        window.dataStore.active_slide = slides_ids.indexOf(clickedSlideIndex); 

        console.log(slides_ids[old_active_slide],clickedSlideIndex)
        updateURL()


        switchMode()
     
    
        change_plotly_static(slides_ids[old_active_slide],true) //old
        change_plotly_static(clickedSlideIndex,false) //new
        
        

       
       
    }
}
});



function switchMode() {
        //change mode
        window.dataStore.mode = (window.dataStore.mode === 'grid') ? 'presentation' : 'grid';
        document.getElementById('slide-container').className = window.dataStore.mode;


        // Hide/Show slides
        const slides = document.querySelectorAll(".slide");

       
        slides.forEach((slide, index) => {
        if (window.dataStore.mode === 'presentation' && index !== window.dataStore.active_slide){
           
            slide.style.visibility = 'hidden'
        } else {
          
            slide.style.visibility = 'visible'
        }

        });
       
         //Make the interactive plot disappear
        updatePlotly()
        //Change the number of rows in grid--------
        function setGridRowsBasedOnN(N) {
          const numberOfRows = Math.ceil(N / 4);
           const gridElement = document.querySelector('.grid');
           gridElement.style.gridTemplateRows = `repeat(${numberOfRows}, 25%)`;

           }

        if (window.dataStore.mode === 'grid'){  
         const N = document.querySelectorAll(".slide").length
         setGridRowsBasedOnN(N);}
        //----------------------------------------

        // Manage interactable elements
        const interactables = document.querySelectorAll('.interactable');
        interactables.forEach(el => {
            el.style.pointerEvents = (window.dataStore.mode === 'grid') ? 'none' : 'auto';
        });

         // Manage PartA and PartB components
         const componentsA = document.querySelectorAll('.PartA');
         componentsA.forEach(component => {
            component.style.visibility = (window.dataStore.mode === 'grid') ? 'hidden' : 'inherit';
         });
 
         const componentsB = document.querySelectorAll('.PartB');
         componentsB.forEach(component => {
             component.style.visibility = (window.dataStore.mode === 'grid') ? 'inherit' : 'hidden';
         });

        

        // Adjust switch button styling
        const switchBtn = document.getElementById('switch-view-btn');
        switchBtn.className = (window.dataStore.mode === 'grid') ? 'button-base button-light' : 'button-base';

        //console.log(window.dataStore.mode)
        //Make the full-screen button disabled
        const fullscreen = document.getElementById('full-screen');
        if (window.dataStore.mode === 'grid'){
            fullscreen.style.visibility = 'hidden'
        } else {
            fullscreen.style.visibility = 'visible'
        }
        

        const aleft = document.getElementById('aleft');
        if (window.dataStore.mode === 'grid'){
            aleft.style.visibility = 'hidden'
        } else {

            aleft.style.visibility = 'visible'
        }
        const aright = document.getElementById('aright');
        if (window.dataStore.mode === 'grid'){
            aright.style.visibility = 'hidden'
        } else {
            aright.style.visibility = 'visible'
        }

        //Adjust model animation
        if (window.dataStore.mode === 'grid'){
           toggleAnimations(false);}
        else { toggleAnimations(true)}   

}


document.getElementById('switch-view-btn').addEventListener('click', function() {
        switchMode();
});

   
function fullScreen() {

    var outerContainer = document.getElementById('slide-container');

    function adjustFontSize() {
        outerContainer.classList.add('fullscreen-mode');
        window.dataStore.mode = 'full';
        window.dataStore.index = 0;
       
        updateEventVisibility()
      
    }
    
    outerContainer.requestFullscreen().then(adjustFontSize);
    

      document.onfullscreenchange = function() {
           if (!document.fullscreenElement) {

                outerContainer.classList.remove('fullscreen-mode');
              
                    window.dataStore.mode = 'presentation';

                    // Show the active slide
                    const slides = document.querySelectorAll(".slide");
                    slides.forEach((slide, index) => {

                    if (index == window.dataStore.active_slide){

                        slide.style.visibility = 'visible'
                    } else {
                        slide.style.visibility = 'hidden'}                
                    })

                   
                    //show all components in presentation mode
                    const components = document.querySelectorAll(".componentA");
                    components.forEach((component, index) => {
                    component.style.visibility = 'inherit'
                    //component.hidden = false;
                     });
    
                };
        
        }

    

}


document.getElementById('full-screen').addEventListener('click', function() {
    fullScreen();
});


});

//Save presentation for self-deployment
function savePresentation() {
    var element = document.documentElement;
    if (!element) {
        console.error('Document element not found.');
        return; // Exit the function if the element is not found
    }
    
    // Serialize the data stored in window.dataStore to a JSON string
    var dataStoreJson = JSON.stringify(window.dataStore || {});
    
    // Create a script tag that will re-initialize window.dataStore with the saved data
    var dataStoreScript = `<script>window.dataStore = ${dataStoreJson};</script>`;
    
    // Capture the entire HTML content
    var htmlContent = element.outerHTML;
    
    // Use a regular expression to remove the specific <script> tag from the HTML content
    // This pattern matches the <script> tag with variations in attribute order, additional attributes, and whitespace
    //var scriptPattern = /<script\s+type=['"]module['"]\s+src=['"]assets\/js\/load\.js['"]\s*><\/script>/g;
    //var modifiedHtmlContent = htmlContent.replace(scriptPattern, '');
    
    // Append the dataStore script to the modified HTML content
    var modifiedHtmlContent = htmlContent.replace('</body>', dataStoreScript + '</body>');
    
    // Debugging: Log the final HTML to ensure it's correct
    //("Final HTML content:", modifiedHtmlContent);

    // Create a Blob with the final HTML content
    var blob = new Blob([modifiedHtmlContent], { type: 'text/html' });
    
    // Create and trigger a download link
    var downloadLink = document.createElement('a');
    downloadLink.href = window.URL.createObjectURL(blob);
    downloadLink.download = 'presentation.html'; // Name of the file to download
    document.body.appendChild(downloadLink);
    downloadLink.click(); // Trigger the download
    document.body.removeChild(downloadLink); // Clean up
}

// Assuming 'download_html' is the ID of the button that triggers the download
//document.getElementById('download_html').addEventListener('click', function() {
//    savePresentation();
//});
