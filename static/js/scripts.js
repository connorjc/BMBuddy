$(document).ready(function(e){
    $('.search-panel .dropdown-menu').find('a').click(function(e) {
        e.preventDefault();
 //       var param = $(this).attr("href").replace("#","");
        var concept = $(this).text();
        $('.search-panel span#search_concept').text(concept);
        $('.input-group #search_crit').val(concept);
 //       $('.input-group #search_param').val(param);
        });

    $('#add_button').click(function() {
      $('#shop-list-dialog').show("fast");
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

    $('#shop-list-add').click(function() {
      var walmart = $('#walmartQuantity').val();
      var costco = $('#costcoQuantity').val();
      
      $.ajax({
        url: "/add_shopping",
        type: "POST",
        data: JSON.stringify({ walmartQuantity: walmart, costcoQuantity: costco,
            upc: $('#product').attr('data-upc') }),
        contentType: "application/json; charset=utf-8",
        success: function(response) { $('#walmartQuantity').val(0); $('#costcoQuantity').val(0); 
            $('#shop-list-dialog').hide(); }
      });

    });

    $('#shop-list-cancel').click(function() {
      $('#shop-list-dialog').hide();
    });

    $(document.body).on('click', '#shop-list-refresh' ,function(){
      var price = parseFloat($(this).parent().parent().find('#row-price').text());
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

      $('#shopping-total').text(newTotal.toFixed(2));

      $.post("update_shopping", { quantity : -1, upc : upc, store : store } );

      $(this).parent().parent().remove();

    });


});
