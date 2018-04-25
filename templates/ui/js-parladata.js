$(document).ready(function() {
/*
PARLADATA JAVASCRIPT V1
*/
        console.log('parladata ready');


/*
NEWSLETTER FORM VALIDATION USING AJAX
*/
        $('#form-newsletter').bind('submit', function (event) {
					console.log('submit');
					event.preventDefault();
          $.ajax({
            type: 'POST',
            url: '{{profile.rooturl}}{{profile.postnewsletter}}',
            data: $('#form-newsletter').serialize(),
						beforeSend: function() {
							console.log('before');
		          $('#submit-newsletter').attr('disabled', true);
		        },
						complete: function() {
							console.log('complete');
	            $('#submit-newsletter').attr('disabled', false);
	          },
            success: function (data) {
							console.log('success');
							$('#form-newsletter').hide();
							$('#ui-newsletter').show().html(data).slideDown();
            }
          });
				});

				$('#ui-newsletter').bind('click', function(event) {
					  console.log('delete');
				    $(this).hide();
				    $('#form-newsletter').show();
				});
/*
*
*/
/*
*   END DOM READY
*/
});



/*
*   BULMA BURGER
*/
document.addEventListener('DOMContentLoaded', function () {
  // Get all "navbar-burger" elements
  var $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {

    // Add a click event on each of them
    $navbarBurgers.forEach(function ($el) {
      $el.addEventListener('click', function () {

        // Get the target from the "data-target" attribute
        var target = $el.dataset.target;
        var $target = document.getElementById(target);

        // Toggle the class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

      });
    });
  }
});
