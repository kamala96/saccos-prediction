// Call the dataTables jQuery plugin


// $(document).ready(function () {
//   $('#dataTable').DataTable();
// });


$(document).ready(function () {
  $('#dataTable').DataTable({
    dom: 'Bfrtip',
    buttons: [
      'copy', 'csv', 'excel', 'pdf', 'print'
    ]
  });
});
