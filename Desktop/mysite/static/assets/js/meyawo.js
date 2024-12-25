/*!
=========================================================
* Meyawo Landing page
=========================================================

* Copyright: 2019 DevCRUD (https://devcrud.com)
* Licensed: (https://devcrud.com/licenses)
* Coded by www.devcrud.com

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// smooth scroll
$(document).ready(function(){
    $(".navbar .nav-link").on('click', function(event) {

        if (this.hash !== "") {

            event.preventDefault();

            var hash = this.hash;

            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 700, function(){
                window.location.hash = hash;
            });
        } 
    });
});

// navbar toggle
$('#nav-toggle').click(function(){
    $(this).toggleClass('is-active')
    $('ul.nav').toggleClass('show');
});

//Show speech in same page
function convertTextToSpeech() {
    const formData = new FormData(document.getElementById('textForm'));
    fetch("{% url 'convert_to_audio' %}", {
        method: 'POST',
        body: formData,
        headers: {'X-CSRFToken': '{{ csrf_token }}'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_file) {
            const player = document.getElementById('audioPlayer');
            player.innerHTML = `<audio controls><source src="${data.audio_file}" type="audio/mpeg">Votre navigateur ne supporte pas l'élément audio.</audio>`;
        }
    })
    .catch(error => console.error('Error:', error));
}