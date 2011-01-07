$(document).ready(function(){
    $.get('/l3ms/nav' + document.location.pathname,
          function(r) { $("#l3msNav").append(r) })
})
