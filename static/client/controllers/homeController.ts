namespace main.controllers {            
    export class HomeController {
        flames: flamber.interfaces.Flames[];
        
        constructor(private $scope: ng.IScope, private $http: ng.IHttpService){

        }
    }
}