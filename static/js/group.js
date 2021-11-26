function create_group(data){
    $.ajax({
        url:"/new-group",
        method:"POST",
        data: data,
        success:function(data){
            Toast.fire({
                icon: "success",
                title: data
            });
            $('#creategroup_list_added').empty();
            $('#create_group_name').val('');
            $('#ip_sfcg').val('');
            $('#myModalAddGroupsChat').modal('hide')
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr.responseText);
            Toast.fire({
                icon: "error",
                title: xhr.responseText
            });
        }
    });
}