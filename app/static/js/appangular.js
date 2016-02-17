app = angular.module('myApp',  ['angularUtils.directives.dirPagination','angularMoment','ngFlash']);

// would throw an undefined error if not in place
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    });

// broadcaster to other controllers
app.run(function($rootScope) {
    $rootScope.$on('handleEmit', function(event, args) {
        $rootScope.$broadcast('handleBroadcast', args);
    });
});

// stores the pagination html
app.config(function(paginationTemplateProvider) {
    paginationTemplateProvider.setPath('static/js/dirPagination.tpl.html');
});

// gets new posts; items depends on rows config
// uses cache to avoid refreshing whole data
app.controller('postController', function($scope, $http,  $sce) {
    $scope.currentPage = 1;
    $scope.pageSize = 10;
    $scope.posts = [];

    $http.get("/get_posts/", {cache: true, params: {rows: 100}})
    .success(function (response) {$scope.posts = response.posts;
    console.log('get_posts',response);
    });

    $scope.$on('handleBroadcast', function(event, args) {
        if (args.from == 'postbox') {
            newpost = args.message.posts;
            console.log('postmessage', newpost);
            // unshift instead of push; it inserts on first index
            $scope.posts.unshift(newpost);
        }
    });
});

// post new entries; has to be json object
app.controller('postboxController', function($scope, $http) {
    $scope.submit = function() {
        newpost = {}
        newpost = {title: $scope.title, body: $scope.body };
        $http.post("/new_post/", {params: newpost})
        .success(function(response){
            $scope.$emit('handleEmit', {from: 'postbox', message: response});
        });
    }
});



// gets from python and storing in scope.script
app.controller('scriptController', function($scope,$http) {
    $scope.$on('handleBroadcast', function(event, args) {
        if (args.from == 'category') {
        $scope.script = []
        $http.get("http://127.0.0.1:5000/filter/script/category_id/" + args.message)
        .success(function (response){
            $scope.script = response;
            console.log('get script data',response);
            });
        }
    });

    // handles click on each rows and broadcast the ids selected
    // to the rootscope broadcaster above
    $scope.filter = function(id) {
        $scope.$emit('handleEmit', {from: 'script', message: id});
    };

    // this is a function that adds rows to the table
    $scope.addScript = function() {
        if ($scope.script === undefined) {
        $scope.counter = 1
        } else {
        $scope.counter = $scope.script.length + 1
        }
        $scope.script.push({'name' : '', 'order' : $scope.counter, 'begingroup' : '', 'join' : '', 'source' : '', 'operator' : ''
        , 'value' : '', 'endgroup' : '', 'datatype' : '', 'description' : '', 'mainparamid' : ''});
         $scope.counter++;
    }

    // saves the clicked index to pass to the delete function
     $scope.selectscript = function(index){
        $scope.selectedscript = index;
    }

    // deletes the selected ids by splicing the subparam collection
     $scope.deletescript = function(index){
     $scope.script.splice( $scope.selectedscript, 1);
    }

});

// gets from python and storing in scope.mainparam
app.controller('mainparamController', function($scope,$http) {
    $scope.$on('handleBroadcast', function(event, args) {
        if (args.from == 'script') {
        $scope.mainparam = []
        $http.get("http://127.0.0.1:5000/filter/mainparam/script_id/" + args.message)
        .success(function (response){
            $scope.mainparam = response;
            console.log('get main param data', response);
            });
        }
    });

    // handles click on each rows and broadcast the ids selected
    // to the rootscope broadcaster above
    $scope.filter = function(id) {
        $scope.$emit('handleEmit', {from: 'mainparam', message: id});
    };

    // this is a function that adds rows to the table
    $scope.addMainparam = function() {
        if ($scope.mainparam === undefined) {
        $scope.counter = 1
        } else {
        $scope.counter = $scope.mainparam.length + 1
        }
        $scope.mainparam.push({'name' : '', 'order' : $scope.counter, 'begingroup' : '', 'join' : '', 'source' : '', 'operator' : ''
        , 'value' : '', 'endgroup' : '', 'datatype' : '', 'description' : '', 'mainparamid' : ''});
         $scope.counter++;
    }

    // saves the clicked index to pass to the delete function
     $scope.selectmainparam = function(index){
        $scope.selectedmainparam = index;
    }

    // deletes the selected ids by splicing the subparam collection
     $scope.deletemainparam = function(index){
     $scope.mainparam.splice( $scope.selectedmainparam, 1);
    }

});

// gets from python and storing in scope.subparam
app.controller('subparamController', function($scope,$http) {
    $scope.$on('handleBroadcast', function(event, args) {
        if (args.from == 'mainparam') {
        $scope.subparam = []
        $http.get("http://127.0.0.1:5000/filter/subparam/mainparam_id/" + args.message)
        .success(function (response){
            $scope.subparam = response;
            console.log('get sub param data', response);
            });
        }
    });

    // this is a function that adds rows to the table
    $scope.addSubparam = function() {
        if ($scope.subparam === undefined) {
        $scope.counter = 1
        } else {
        $scope.counter = $scope.subparam.length + 1
        }
        $scope.subparam.push({'name' : '', 'order' : $scope.counter, 'begingroup' : '', 'join' : '', 'source' : '', 'operator' : ''
        , 'value' : '', 'endgroup' : '', 'datatype' : '', 'description' : '', 'mainparamid' : ''});
         $scope.counter++;
    }

    // saves the clicked index to pass to the delete function
     $scope.selectsubparam = function(index){
        $scope.selectedsubparam = index;
    }

    // deletes the selected ids by splicing the subparam collection
     $scope.deleteSubparam = function(index){
     $scope.subparam.splice( $scope.selectedsubparam, 1);
    }

});

// UPDATES DOM

app.directive('contenteditable',function() { return {
    require: 'ngModel',
    link: function(scope, element, attrs, ctrl) {
        // view -> model
        element.bind('input', function() {
            scope.$apply(function() {
                ctrl.$setViewValue(element["0"].tagName=="INPUT" ? element.val() : element.text());
                scope.watchCallback(element.attr('ng-model'));
            });
          });
        // model -> view
        ctrl.$render = function() {
            element.text(ctrl.$viewValue);
            element.val(ctrl.$viewValue);
        };
     }};
});


// SEARCH functionality

function searchtable(tablename) {
    var searchTerm = $(".search" + tablename).val();
    var listItem = $('.' + tablename + 'hits tbody').children('tr');

    var searchSplit = searchTerm.replace(/ /g, "'):containsi('")

  $.extend($.expr[':'], {'containsi': function(elem, i, match, array){
        return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
    }
  });

  $("." + tablename + "hits tbody tr").not(":containsi('" + searchSplit + "')").each(function(e){
    $(this).attr('visible','false');
  });

  $("." + tablename + "hits tbody tr:containsi('" + searchSplit + "')").each(function(e){
    $(this).attr('visible','true');
  });

  var jobCount = $('.' + tablename + 'hits tbody tr[visible="true"]').length;
    $('.counter').text(jobCount + ' item');

  if(jobCount == '0') {$('.no-result').show();}
    else {$('.no-result').hide();}
}

$(document).ready(function() {
  $(".searchcategory").keyup(function () {
    searchtable("category");
    });
});

$(document).ready(function() {
  $(".searchscript").keyup(function () {
    searchtable("script");
    });
});

$(document).ready(function() {
  $(".searchmainparam").keyup(function () {
    searchtable("mainparam");
    });
});

$(document).ready(function() {
  $(".searchsubparam").keyup(function () {
    searchtable("subparam");
    });
});


