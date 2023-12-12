'use strict';

// 打开弹窗
function init (cut_size) {
	var sizeArr = [0, 0];
	var aspectRatio = null;
	if (cut_size) {
		sizeArr = cut_size.split('*');
		var w = sizeArr[0] * 1;
		var h = sizeArr[1] * 1;

		if (w > h) {
			aspectRatio = (w / h) / 1;
		} else {
			aspectRatio = 1 / (h / w);
		}
	}
}
$('.size_btn').on('click',function (e){
	init($(this).attr('value'));
	$('.popup-wrap').addClass('on');
});
// 关闭弹窗
$('#closeBtn').on('click',function(){
	closeFn();
});

function closeFn (){
	$('.popup-wrap').removeClass('on');
	$('#imageId').cropper("destroy");
}

// 初始化



	$('#imageId').cropper({
		viewMode: 1,
		dragMode: 'none',
		initialAspectRatio: 1,
		preview: '.previewBox',
		// 是否在容器上显示网格背景
		background: true,
		// 定义自动剪裁区域的大小
		// autoCropArea: 1,
		// 是否允许鼠标 缩放图片
		zoomOnWheel: false,
		// 是否允许改变剪裁框的大小
		cropBoxResizable:true,
		// 是否可以移动裁剪框
		cropBoxMovable:true,
		// 是否允许旋转图片
		rotatable: true,
		aspectRatio:aspectRatio
		// 初始化时，自动裁剪图片
		// autoCrop:true,
	})


	// 角度
	var deg = 0;
	//向左旋转
	$("#btnLeft").on("click",function () {
		rotateFn(1)
	});
	//向右旋转
	$("#btnRight").on("click",function () {
		rotateFn(2)
	});

	//换向
	var flagX = true;
	$("#btnScale").on("click",function () {
		if(flagX){
			$('#imageId').cropper("scaleX", -1);
			flagX = false;
		}else{
			$('#imageId').cropper("scaleX", 1);
			flagX = true;
		}
		flagX != flagX;
	});

	//复位
	$("#btnInit").on("click",function () {
		$('#imageId').cropper("reset");
	});


	// 放大
	$("#btnLarge").on("click",function () {
		$('#imageId').cropper("zoom",0.1);
	});
	
	// 缩小
	$("#btnSmall").on("click",function () {
		$('#imageId').cropper("zoom",-0.1);
	});





	
	// 旋转
	function rotateFn (type){
		if(type ==1){
			deg += 90;
		} else {
			deg -= 90;
		}

		$('#imageId').cropper("rotate", deg);
	}


	//图像上传
	function selectImg(file) {
		if (!file.files || !file.files[0]){
				return;
		}
		var reader = new FileReader();
		reader.onload = function (evt) {
				var replaceSrc = evt.target.result;

				//更换cropper的图片
				$('#imageId').cropper('replace', replaceSrc,false);//默认false，适应高度，不失真
				
		}
		reader.readAsDataURL(file.files[0]);
	}

	//裁剪后的处理
	$("#btnSubmit").on("click",function () {
			if ($("#imageId").attr("src") == null ){
				return false;
			}else{
					var cas = $('#imageId').cropper('getCroppedCanvas');//获取被裁剪后的canvas
					var base64url = cas.toDataURL('image/png'); //转换为base64地址形式


				$('#imgBoxId').attr('src',base64url)
				closeFn()

					// ajax 上传图片
					// var formData = new FormData();
					// var file = base64toFile(base64url)
					// formData.append('__avatar1',file );

					// $.ajax({
					// 	type:'post',
					// 	url: '/index.php?r=news/imgupload/toupload',
					// 	cache: false,
					// 	data: formData,
					// 	processData: false,
					// 	contentType: false,
					// 	dataType:'json',
          // }).then(function(res) {
					// 	console.log(res,'-------上传成功')
						
          // }).fail(function(err){ console.log(err)})
			}
	});

	// base64 to file
	function base64toFile  (dataurl)  {
		
			const arr = dataurl.split(',');
			const mime = arr[0].match(/:(.*?);/)[1];
			const suffix = mime.split('/')[1];
			const bstr = atob(arr[1]);
			let n = bstr.length;
			const u8arr = new Uint8Array(n);
			while (n--) {
				u8arr[n] = bstr.charCodeAt(n);
			}
			const file = new File([u8arr], `__avatar1`, {
				type: mime
			});

			return file;
	}
