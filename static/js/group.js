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
function change_conversation_name(conversation_id){
    let conversation_newname
    Swal.fire({
        title: "Đổi tên cuộc trò chuyện",
        input: 'text',
        showCancelButton: true,
        inputPlaceholder: "Nhập tên bạn muốn đổi thành",
        showLoaderOnConfirm: true,
        preConfirm: (value) => {
            conversation_newname = value
            return $.ajax({
                data: {name: value},
                method: "POST",
                url: '/conversation/'+conversation_id+'/rename'
            }).then(response => {
                return response
            }).catch(error => {
                console.log(error)
                Swal.showValidationMessage(
                  'Lỗi: '+error.responseText
                )
            })
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Toast.fire({
                icon: "success",
                title: result.value
            })
            changed_conversation_name(conversation_id, conversation_newname)
        }
    })
}
function changed_conversation_name(conversation_id, conversation_newname){
    let conversation = $("#conversation_list").find("#c_"+conversation_id);
    $(conversation).find("#conversation_title").text(conversation_newname)
    if($("#conversation_item").data("conversation") == conversation_id) {
        $('#c_info_name').text(conversation_newname)
        $('#chatter_displayname').text(conversation_newname)
    }
}
function change_conversation_avatar(conversation_id) {
    Swal.fire({
        title: "Đổi ảnh nhóm",
        input: 'file',
        showCancelButton: true,
        inputPlaceholder: "Nhập tên bạn muốn đổi thành",
        showLoaderOnConfirm: true,
        inputAttributes: {
            'accept': 'image/*',
            'aria-label': 'Upload your group picture'
        },
        preConfirm: (value) => {
            var form_data = new FormData(); 
            form_data.append('file', value);
            console.log(value)
            return $.ajax({
                data: form_data,
                method: "POST",
                url: '/conversation/'+conversation_id+'/change-avatar',
                processData: false,
                contentType: false,
            }).then(response => {
                return response
            }).catch(error => {
                console.log(error)
                Swal.showValidationMessage(
                  'Lỗi: '+error.responseText
                )
            })
        },
    }).then((result) => {
        if (result.isConfirmed) {
            console.log(result)
            changed_conversation_avatar(conversation_id, "static/"+result.value)
        }
    })
}
function changed_conversation_avatar(conversation_id, conversation_avatar){
    let conversation = $("#conversation_list").find("#c_"+conversation_id);
    $(conversation).find("#conversation_image").attr('src', conversation_avatar)
    if($("#conversation_item").data("conversation") == conversation_id) {
        $('#c_info_avatar').attr('src', conversation_avatar)
        $('#chatter_avatar').attr('src', conversation_avatar)
        $("#message_list").css('background-image', 'url('+conversation_avatar+')')
    }
}
function showImagePreview(element) {
    var src = $(element).attr('src');
    var w = 1280;
    var h = 720;
    var left = (window.screen.width / 2) - ((w / 2) + 10);
    var top = (window.screen.height / 2) - ((h / 2) + 50);
    window.open(src,'_blank',
        "status=no,height=" + h + ",width=" + w + ",resizable=yes,left="
        + left + ",top=" + top + ",screenX=" + left + ",screenY="
        + top + ",toolbar=no,menubar=yes,scrollbars=no,location=no,directories=no").focus();
}

function prepare_add_member(conversation_id) {
    
    Swal.fire({
        title: "Thêm thành viên vào nhóm",
        input: 'text',
        html: '<div></div>',
        showCancelButton: true,
        inputPlaceholder: "Nhập tên người dùng",
        didOpen: () => {
            const input = Swal.getInput()
            const html = Swal.getHtmlContainer()
            $(input).keyup($.debounce(500, function(e) {
                Swal.showLoading()
                $.ajax({
                    url:"/new-chat/friends",
                    data: {name: input.value},
                    method:"POST",
                    success:function(data){ 
                        if(data) {
                            Swal.hideLoading()
                            data = JSON.parse(data)
                            $(html).empty();
                            data.forEach(friend => {
                                data_fr = friend['friend_info']
                                let avatar = $('<img class="avatar-circle" src="/static/'+data_fr['avatar']+'">')
                                let username = $('<span class="h6 font-weight-bold">'+data_fr['displayname']+'</span>')
                                let tag = $('<br><span class="h7 font-italic">@'+data_fr['username']+'</span>')
                                let button = $('<div class="ml-auto"><button class="btn btn-success">THÊM</button></div>')
                                var item = $('<div data-id='+data_fr['_id']['$oid']+' class="d-flex my-1 align-items-center"></div>')
                                let info = $('<div class="mx-1"></div>').append(username).append(tag)
                                
                                $(button).on('click', function(){
                                    Swal.showLoading()
                                    $.ajax({
                                        url:"/conversation/"+conversation_id+"/add_member",
                                        data: {user_id: $(item).data('id')},
                                        method:"POST",
                                        success:function(data){ 
                                            Swal.hideLoading()
                                            if(data) {
                                                Swal.close()
                                                Toast.fire({
                                                    icon: "success",
                                                    title: data.message
                                                })
                                            }
                                        },
                                        error: function (xhr, ajaxOptions, thrownError) {
                                            console.log(xhr);
                                            Swal.hideLoading()
                                            Swal.showValidationMessage(
                                                'Lỗi: '+xhr.responseText
                                            )
                                        }
                                    });
                                })
                                $(item).append(avatar)
                                $(item).append(info)
                                $(item).append(button)
                                
                                $(html).append(item)
                                $(html).addClass('text-left')
                            });
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        Swal.hideLoading()
                        Swal.showValidationMessage(
                            'Lỗi: '+xhr.responseText
                        )
                        console.log(xhr);
                    }
                });
            }));
        },
    })
}
function change_nickname(conversation_id, user_id, nickname, username, avatar){
    let html = $('<div></div>')
    html.append($('<img class="avatar-circle-lg mx-auto" src="/static/'+avatar+'">'))
    html.append($('<div class="mx-auto"><span class="h5 font-weight-bold">'+nickname+'</span><br><span class="h7 font-italic">@'+username+'</span></div>'))

    let new_nickname
    Swal.fire({
        title: "Đổi biệt danh thành viên",
        input: 'text',
        showCancelButton: true,
        html: html,
        inputPlaceholder: "Nhập tên bạn muốn đổi thành",
        showLoaderOnConfirm: true,
        preConfirm: (value) => {
            new_nickname = value
            return $.ajax({
                data: {user_id: user_id, nickname: new_nickname},
                method: "POST",
                url: '/conversation/'+conversation_id+'/nickname'
            }).then(response => {
                return response
            }).catch(error => {
                console.log(error)
                Swal.showValidationMessage(
                  'Lỗi: '+error.responseText
                )
            })
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Toast.fire({
                icon: "success",
                title: result.value.message
            })
            console.log(result.value)
        }
    })
}
function kick_from_conversation(conversation_id, user_id, nickname, username, avatar){
    let html = $('<div></div>')
    html.append($('<img class="avatar-circle-lg mx-auto" src="/static/'+avatar+'">'))
    html.append($('<div class="mx-auto"><span class="h5 font-weight-bold">'+nickname+'</span><br><span class="h7 font-italic">@'+username+'</span></div>'))

    Swal.fire({
        title: "Bạn có chắc chắn muốn xoá người này khỏi nhóm?",
        showCancelButton: true,
        html: html,
        showLoaderOnConfirm: true,
        preConfirm: (value) => {
            new_nickname = value
            return $.ajax({
                data: {user_id: user_id},
                method: "POST",
                url: '/conversation/'+conversation_id+'/kick-member'
            }).then(response => {
                return response
            }).catch(error => {
                console.log(error)
                Swal.showValidationMessage(
                  'Lỗi: '+error.responseText
                )
            })
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Toast.fire({
                icon: "success",
                title: result.value
            })
        }
    })
}
function leave_conversation(conversation_id){
    Swal.fire({
        title: "Bạn có chắc chắn muốn rời khỏi nhóm?",
        showCancelButton: true,
        showLoaderOnConfirm: true,
        preConfirm: () => {
            return $.ajax({
                data: {conversation_id: conversation_id},
                method: "POST",
                url: '/conversation/'+conversation_id+'/leave'
            }).then(response => {
                return response
            }).catch(error => {
                console.log(error)
                Swal.showValidationMessage(
                  'Lỗi: '+error.responseText
                )
            })
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Toast.fire({
                icon: "success",
                title: result.value
            })
        }
    })
}