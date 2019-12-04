var $form = $('.register');

$form.on('keyup', 'input', function (e) {
  var $this = $(this),
  $input = $this.val();
  if ($input.length > 0) {
    $form.find('label').addClass('active');
    $form.find('button').addClass('active');
    console.log(e);
    if (e.which === 13) {
      $form.find('button').click();
      $this.blur();
    }
    $(this).addClass('active');
  } else {
    $form.find('label').removeClass('active');
    $form.find('button').removeClass('active');
    $(this).removeClass('active');
  }
});

$form.on('click', 'button.active', function (e) {
  e.preventDefault;
  var $this = $(this);
  $(this).addClass('full');
  $(this).html('Thanks!');

  setTimeout(() => {
    $form.find('input').val('').removeClass('active');
    $form.find('label').removeClass('active');
    $this.removeClass('full active');
    $this.html('OK');
  }, 1200);
});