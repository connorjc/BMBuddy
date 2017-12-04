$(document).ready(function(e){
    $('.search-panel .dropdown-menu').find('a').click(function(e) {
        e.preventDefault();
 //       var param = $(this).attr("href").replace("#","");
        var concept = $(this).text();
        $('.search-panel span#search_concept').text(concept);
        $('.input-group #search_crit').val(concept);
 //       $('.input-group #search_param').val(param);
    });

    $('#resident-list .dropdown-menu').find('a').click(function(e) {
        e.preventDefault();
        var resident = $(this).text();
        $('#resident-list span#resident_selection').text(resident);
    });
    
    $('#HouseList').find('a').click(function(e) {
        e.preventDefault();
 //       var param = $(this).attr("href").replace("#","");
        var concept = $(this).text();
        $('.house-panel span#house_selection').text(concept);
        $('#house_user').val(concept);
 //       $('.input-group #search_param').val(param);
        });


    $('.add_button').click(function() {
      var type = $(this).attr("data-type");
      if (type == "shopping") {
        $('.add-list-dialog').show("fast");
      } else {
        $('#resident_selection').text('Select Name'); 
        $('#wish-list-add-dialog').show("fast");
      }
    });

    $('#search-button').click(function() {
      var param = $("#search_param").val();
      var crit = $("#search_crit").val();

      if ( crit == "UPC" && param && /^[0-9]+$/.test(param))
      {
        document.getElementById("search-form").submit();
      } else if ( crit == "Name" && param ) { 
        document.getElementById("search-form").submit();
      } else {
        $("#search-warning").fadeIn(500).delay(7*1000).fadeOut(500);
      }

    });

    $('#list-add').click(function() {
      var walmart = $('#walmartQuantity').val();
      var costco = $('#costcoQuantity').val();
      var type = $('.add-list-dialog').attr('data-type') 
      $.ajax({
        url: "/add_shopping",
        type: "POST",
        data: JSON.stringify({ walmartQuantity: walmart, costcoQuantity: costco,
          upc: $('#product').attr('data-upc') }),
        contentType: "application/json; charset=utf-8",
        success: function(response) { $('#walmartQuantity').val(0); $('#costcoQuantity').val(0); 
          $('.add-list-dialog').hide(); }
      }); 
    });

    $('#wish-list-add-confirm').click(function() {

      var type = $('#wish-list-add-dialog').attr("data-type");
      var resident = $('#resident_selection').text();
      var upc = $('#wish-list-add-dialog').attr("data-active-upc");

      var result;

      if (resident == "Select Name") {
        $('#vote-error').show('fast');
      } else {
        $.ajax({
          url: "/add_wish",
          type: "POST",
          data: JSON.stringify({ resident: resident, type: type, upc: upc }),
          contentType: "application/json; charset=utf-8",
          success: function(response) {
            if (response == "1")
              $('vote-error-update').show('fast');
          }
        });
      }
      $('#wish-list-add-dialog').hide();
    });

    $(document.body).on('click', '#list-cancel' ,function(){
      var id = $(this).attr('data-type');
      if (id == "wish")
        $('#wish-list-add-dialog').hide();
      else
        $('.add-list-dialog').hide();
    });

    $(document.body).on('click', '#shop-list-refresh' ,function(){
      var price = parseFloat($(this).parent().parent().find('.row-price').text());
      var quantity = parseFloat($(this).parent().parent().find('.row-quantity').val());
      var upc = $(this).parent().parent().find('#row-name').attr('data-upc');
      var store = $(this).parent().parent().find('#row-store').text();
      $(this).parent().parent().find('.row-subtotal').text((price * quantity).toFixed(2));

      
      var sum = 0;
      var count = 0;

      $('.row-subtotal').each(function(){
        sum += parseFloat($(this).text());
        count += 1;
      });

      var budget = $('#shopping-total').attr('data-budget')
      if (sum > budget)
        $('#shopping-total').parent().attr('class','text-danger');
      else if (sum < (budget - 50))
        $('#shopping-total').parent().attr('class','text-success');
      else if (budget)
        $('#shopping-total').parent().attr('class','text-warning');

      $('#shopping-total').text(sum.toFixed(2));

      if (upc)
        $.post("update_shopping", { quantity : quantity, upc : upc, store : store } );
    });

    $(document.body).on('click', '#shop-list-remove' ,function(){
      
      var upc = $(this).parent().parent().find('#row-name').attr('data-upc');
      var subtotal = parseFloat($(this).parent().parent().find('.row-subtotal').text());
      var store = $(this).parent().parent().find('#row-store').text();

      
      var prevTotal = parseFloat($('#shopping-total').text());

      var newTotal = prevTotal - subtotal;

      var budget = $('#shopping-total').attr('data-budget')
      if (newTotal > budget)
        $('#shopping-total').parent().attr('class','text-danger');
      else if (newTotal < (budget - 50))
        $('#shopping-total').parent().attr('class','text-success');
      else
        $('#shopping-total').parent().attr('class','text-warning');

      $('#shopping-total').text(newTotal.toFixed(2));

      $.post("update_shopping", { quantity : -1, upc : upc, store : store } );

      $(this).parent().parent().remove();

    });

    $(document.body).on('click', '.wish-list-voteup', function(){
      
      var upc = $(this).parent().parent().attr('data-upc');
      var subtotal = parseInt($(this).parent().parent().find('.row-votes').text());
    
      $("#wish-list-vote-dialog").attr("data-type","up");
      $("#wish-list-vote-dialog").attr("data-upc",upc);
      $('#resident_selection').text('Select Name');
      $('#vote-error').hide();
      $('#vote-error-update').hide();
      $("#vote-title").text("Vote Up"); 
      $("#wish-list-vote-dialog").attr("data-active-upc",upc);
      $("#wish-list-vote-dialog").show("fast");
      $(this).parent().parent().attr('id','active');
    });

    $(document.body).on('click', '.wish-list-votedown', function(){
     
      var upc = $(this).parent().parent().attr('data-upc');
      var subtotal = parseInt($(this).parent().parent().find('.row-votes').text());
    
      $("#wish-list-vote-dialog").attr("data-type","down");
      $("#wish-list-vote-dialog").attr("data-upc",upc);
      $('#resident_selection').text('Select Name');
      $('#vote-error').hide();
      $('#vote-error-update').hide();
      $("#vote-title").text("Vote Down"); 
      $("#wish-list-vote-dialog").attr("data-active-upc",upc);
      $("#wish-list-vote-dialog").show("fast");
      $(this).parent().parent().attr('id','active');
    });

    $(document.body).on('click', '.wish-list-add' ,function(){
      var wPrice = $(this).parent().parent().find('.walmart').text();
      var cPrice = $(this).parent().parent().find('.costco').text();
      $('#wish-add-walmart-price').text(wPrice);
      $('#wish-add-costco-price').text(cPrice);
      $('.add-list-dialog').show('fast');
    });


    $(document.body).on('click', '.wish-list-remove' ,function(){
      
      var upc = $(this).parent().parent().attr('data-upc');

      var result;

      $.ajax({
        url: "/update_wish",
        type: "POST",
        data: JSON.stringify({ type: "delete", upc: upc }),
        contentType: "application/json; charset=utf-8",
        success: function(response) { }
      });
      
      $(this).parent().parent().remove();

    });

  $('#wish-list-vote-confirm').click(function() {
    var type = $('#wish-list-vote-dialog').attr("data-type");
    var resident = $('#resident_selection').text();
    var upc = $('#wish-list-vote-dialog').attr("data-active-upc");

    var result;

    if (resident == "Select Name") {
      $('#vote-error').show('fast');
    } else {

      $.ajax({
        url: "/update_wish",
        type: "POST",
        data: JSON.stringify({ resident: resident, type: type, upc: upc }),
        contentType: "application/json; charset=utf-8",
        success: function(response) {
          if (type == "up") {
            var votes = parseInt($('#active .row-votes').text()) + 1;
            $('#active .row-votes').text(votes);
            $('#active').removeAttr('id');
          } else {
            var votes = parseInt($('#active .row-votes').text()) - 1;
            $('#active .row-votes').text(votes);
            $('#active').removeAttr('id');
          }
        }
      });

    }
    $('#wish-list-vote-dialog').hide();
  });

   $('#wish-list-vote-cancel').click(function() {
      $('#wish-list-vote-dialog').hide();
    });

});
