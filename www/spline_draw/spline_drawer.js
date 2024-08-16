import * as THREE from "three";

// general setup, boring, skip to the next comment
var scene = new THREE.Scene();
    scene.background = new THREE.Color( 'black' );

var camera = new THREE.OrthographicCamera( -innerWidth/2, innerWidth/2, innerHeight/2, -innerHeight/2, -10, 10 );
    camera.position.set( 0, 0, 10 );
    camera.lookAt( scene.position );

var renderer = new THREE.WebGLRenderer( {antialias: true} );
    renderer.setSize( innerWidth, innerHeight );
    document.body.appendChild( renderer.domElement );
			
window.addEventListener( "resize", (event) => {
    camera.updateProjectionMatrix( );
    renderer.setSize( innerWidth, innerHeight );
		renderer.render( scene, camera );
});


// next comment
// create a spline curve and a line to visualize it
var curve = new THREE.SplineCurve( [] ),
		spline = new THREE.Line( 
				new THREE.BufferGeometry(),
				new THREE.LineBasicMaterial( { color: 'skyblue' } )
		);

scene.add( spline );
renderer.render( scene, camera);

var x_udp, y_udp, z_udp;
var t=setInterval(clear_scene,10000);

while(true) {
	var promise1 = new Promise(function(resolve, reject) {
		var xhr = new XMLHttpRequest(),
			method = "GET",
			url = "http://127.0.0.1:8001/position";
	
		xhr.open(method, url, true);
		xhr.onreadystatechange = function() {
			if (xhr.readyState === 4 && xhr.status === 200) {
			resolve(JSON.parse(xhr.responseText));
			}
		};
		xhr.send();
		});

	promise1.then(function(value) {
        x_udp = parseInt(value[0])
        y_udp = parseInt(value[1])
        z_udp = parseInt(value[2])
    });

	// click coordinates
	var x = parseInt(197 - x_udp), y = parseInt(y_udp/2);
	// console.log(x, y)

	// draw a black circle to indicate dot position
	var point = new THREE.Mesh(
					new THREE.CircleGeometry( 5 ),
					new THREE.MeshBasicMaterial( {color: 'yellow' })
			)
			point.position.set( x, y, 0 );
			scene.add( point );

	// add the point to the curve
	curve.points.push( new THREE.Vector2(x,y) );
	curve = new THREE.SplineCurve( curve.points );
	var points = curve.getPoints( 20*curve.points.length );

	// regenerate its image
	spline.geometry.dispose( );
	spline.geometry = new THREE.BufferGeometry();
	spline.geometry.setFromPoints( points );

	renderer.render( scene, camera );
	await sleep(10)
}

function clear_scene(){
	location.reload();
}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
  }


