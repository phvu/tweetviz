var container;
var camera, controls, scene, renderer;

var mouse = new THREE.Vector2();
var mouseDownContent = '';
var raycaster = new THREE.Raycaster();
var INTERSECTED;
var SELECTED;

var info, info_stick;

function init() {

    container = document.getElementById( "container" );

    info = document.getElementById( 'info' );
    info_stick = document.getElementById( 'info_stick' );

    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 10000 );
    camera.position.z = 50;

    controls = new THREE.TrackballControls( camera );
    controls.rotateSpeed = 1.0;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 0.8;
    controls.noZoom = false;
    controls.noPan = true;
    controls.staticMoving = false;
    controls.dynamicDampingFactor = 0.3;

    scene = new THREE.Scene();

    pickingScene = new THREE.Scene();
    pickingTexture = new THREE.WebGLRenderTarget( window.innerWidth, window.innerHeight );
    pickingTexture.minFilter = THREE.LinearFilter;
    pickingTexture.generateMipmaps = false;

    scene.add( new THREE.AmbientLight( 0xffffff ) );

    var lights = [];
    lights[0] = new THREE.PointLight( 0xffffff, 1, 0 );
    lights[1] = new THREE.PointLight( 0xffffff, 1, 0 );
    lights[2] = new THREE.PointLight( 0xffffff, 1, 0 );

    lights[0].position.set( 0, 100, 0 );
    lights[1].position.set( 50, 100, 100 );
    lights[2].position.set( -50, -100, -50 );

    scene.add( lights[0] );
    scene.add( lights[1] );
    scene.add( lights[2] );

    // var geometry = new THREE.Geometry(),
    // pickingGeometry = new THREE.Geometry(),
    // pickingMaterial = new THREE.MeshBasicMaterial( { vertexColors: THREE.VertexColors } ),
    // defaultMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff, shading: THREE.FlatShading, vertexColors: THREE.VertexColors } );

    var geom = new THREE.SphereGeometry( 0.4, 16, 16 );

    for ( var i = 0; i < tweets.length; i ++ ) {

        // var obj = new THREE.Mesh( geom, new THREE.MeshLambertMaterial( { color: Math.random() * 0xffffff } ) );
        var obj = new THREE.Mesh( geom, new THREE.MeshLambertMaterial( { color: 0x1e2855, shading: THREE.SmoothShading } ) );

        obj.position.x = tweets[i].x;
        obj.position.y = tweets[i].y;
        obj.position.z = tweets[i].z;
        obj.idx = i;

        scene.add(obj);
    }

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setClearColor( 0xf0f0f0 );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.sortObjects = false;
    container.appendChild( renderer.domElement );

    renderer.domElement.addEventListener( 'mousemove', onMouseMove, false );
    renderer.domElement.addEventListener( 'mousedown', onMouseDown, false );
    window.addEventListener( 'resize', onWindowResize, false );
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function onMouseMove( e ) {
    mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
    mouse.y = - ( (event.clientY) / window.innerHeight ) * 2 + 1;
}

function onMouseDown( e ) {
    raycaster.setFromCamera( mouse, camera );
    var intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length > 0) {
        if (SELECTED != intersects[0].object) {
            if (SELECTED) {
                SELECTED.material.emissive.setHex(SELECTED.currentHexSelect);
            }
        }
        SELECTED = intersects[0].object;
        SELECTED.currentHexSelect = SELECTED.currentHex;
        SELECTED.material.emissive.setHex(0x00ff00);
        tweet_obj = tweets[SELECTED.idx];
        info_stick.innerHTML = tweet_obj.tweet +
        ' [<a target="_blank" href="http://twitter.com/' + userName + '/status/' + tweet_obj.id + '">Link</a>]';
    } else {
        if (SELECTED) {
            SELECTED.material.emissive.setHex(SELECTED.currentHexSelect);
        }
        SELECTED = null;
        info_stick.innerHTML = '<i>Click on any point to stick the corresponding tweet here</i>';
    }
}

function animate() {

    requestAnimationFrame( animate );

    render();
}

function pick() {
    raycaster.setFromCamera( mouse, camera );
    var intersects = raycaster.intersectObjects( scene.children );

    if ( intersects.length > 0 ) {
        if ( INTERSECTED != intersects[ 0 ].object ) {
            if ( INTERSECTED && INTERSECTED != SELECTED) {
                INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex );
            }

            INTERSECTED = intersects[ 0 ].object;
            INTERSECTED.currentHex = INTERSECTED.material.emissive.getHex();
            if (INTERSECTED != SELECTED) {
                INTERSECTED.material.emissive.setHex( 0xff0000 );
            }
            info.innerHTML = tweets[INTERSECTED.idx].tweet;
        }
    } else {
        if ( INTERSECTED && INTERSECTED != SELECTED) {
            INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex );
        }
        INTERSECTED = null;
        info.innerHTML = '<i>Hover on the points to see the tweets</i>';
    }
}

function render() {
    controls.update();
    pick();
    renderer.render( scene, camera );
}