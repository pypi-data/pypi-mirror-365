v1.0.0 - Beta code release <br>

v1.0.1 - BSD-3 license, expanded ground-truth docs, show line-credits, miscellaneous fixes <br>

v1.0.2 - New documentation, plant improvements, disk and reproducibility improvements <br>

v1.0.3
- Fluid code release
- implementing assets documentation
- render tools improvements
- integration testing script

v1.0.4 
- Tools and docs to download preliminary pre-generated data release, 
- Reformat "frames" folder to be more intuitive / easier to dataload
- ground truth updates
- render throughput improvements

v1.1.0
- Update to blender 3.6, install blender either via pip or standalone
- Restructure project into an `infinigen` python package and `infinigen_examples` directory
- Add unit tests

v1.2.0
- Integrate OcMesher terrain option - see https://github.com/princeton-vl/OcMesher

v1.2.4
- Fix TreeFactory crash for season='winter'

v1.2.5
- Add Terrain.populated_bounds parameters
- Fix reinitalizing terrain

v1.2.6
- Fix bug where manage_jobs.py would pick a random scene_type config even if one was already loaded
- Fix bug where manage_jobs.py would ignore CUDA_VISIBLE_DEVICES that didnt start at 0
- Add NotImplementedError for dynamic hair.

v1.3.1
- Fix configuration bug causing massive render slowdown 
- Create noisier video trajectories optimized for training

v1.3.2
- Bugfix USD/OBJ exporter, add export options to generate_individual_assets

v1.3.3
- Bugfix camera code to allow multiple cameras, prevent all-water frames
- Tweak rendering settings
- Tweak test lists & add timeouts, pass all tests

v1.3.4
- Fixed bug where individual export would fail on objects hidden from viewport
- Fixed Terrain.populated_bounds bad merge

v1.4.0 - Infinigen Indoors
- Add library of procedural generators for indoor objects & materials
- Add indoor scene generation system, including constraint language and solver
- Add HelloRoom.md & ExportingToSimulators.md

v1.4.1
- @David-Yan1 fix placeholder & ocmesher submodule version
- @lahavlipson fix bug in surface normals of wall meshes
- @araistrick bugfix example commands & other typos

v1.5.0
- ruff & auto-lint-fix the entire codebase
- move mesh assets into infinigen/assets/objects
- minimize pip dependences: remove unused packages & move terrain/gt-vis packages into optional \[terrain,vis\] extras.
- add parameters for object clutter, reduce excessively cluttered / slow indoors scenes
- minorly improve infinigen-indoors performance via logging & asset hiding

v1.5.1
- Fix "base.gin" crash in generate_individual_assets
- Fix individual_export in export.py
- Fix Dockerfile
- Remove dependabot
- Add scatter unit tests and fix scatter imports
- Fix black renders due to non-hidden particle emitter

v1.6.0
- Add geometric tile pattern materials
- Tune window parameters and materials
- Add floating object placement generator and example command
- Add logging to terrain asset creation & simulations 
- Add packaged font files to assets/fonts, fix too-many-open-fonts crash
- Fix fish school disappearing at last frame in video
- Fix crash from `fabrics.apply`

v1.7.0
- Implement camera IMU calculation and export
- Add point tracking ground truth

v1.7.1
- Bugfix fine terrain in arctic scenes

v1.8.0
- Implement tools for importing external assets into Indoors
- Use constraint language to configure room solving
- Add pillars, vertically split wall materials

v1.8.1
- Fix bug causing hard constraints on scalar inequalities (e.g distance > x) to be ignored
- Fix bug causing livingroom sofa alignment to be incorrect
- Fix bias in camera trajectory starting direction
- Improve visual quality of home.py via constraint tweaks and new generate_indoors stages
- Fix silent output from upload stage, remove export from upload
- Reduce solving time spent on small objects

v1.8.2
- Remove nonessential opengl_gt packages
- Fix CrabFactory crash, FruitContainerFactory unparent object, wall parts
- Fix nature particles not visible in render
- Add smbpy du and df commands
- Fix fineterrain not included in export for optimize_diskusage=True
- Update mesher_backend config name & default commands

v1.8.3
- Fix landlab import error message, add no_landlab.gin config

v1.9.0
- Add CoPlanar indoor constraint, fix backwards tvs/monitors/sinks
- Fix empty scene / null objects selected during export
- Add full system visual check / integration script

v1.9.1
- Reduce excessive polycount in bottles and tableware objects
- Fix alignment of windows
- Fix wall materials not being deterministic w.r.t random seed
- Fix gin configs not correctly passed to slurm jobs in generate_individual_assets
- Fix integration test image titles 
- Fix integration test asset image alignment
- Make multistory houses disabled by default

v1.10.0
- Add Configuring Cameras documentation
- Add config for multiview cameras surrounding a point of interest
- Add MaterialSegmentation output pass
- Add passthrough mode to direct manage_jobs stdout directly to terminal
- Add "copyfile:destination" upload mode

v1.10.1
- Fix missing validity checks for camera-rig cameras which are not the 0th index
- Fix missing seat in dining chair

v1.11.0
- Update to Blender == 4.2.0

v1.11.1
- Fix failed camera search when canyon/cliff/cave loaded as nature background
- Fix scrambled GT maps in blender_gt due to incorrect OpenEXR pixel unpack ordering
- Fix save_mesh kwarg mismatch from v1.10.0
- Remove `frozendict` dependency, make `geomdl` optional if not using creatures
- Make `submitit` optional if not using SLURM
- Make blender addons optional if not using relevant assets (rocks/terrain/snowlayer)
- Make `bnurbs` CPython module optional and not installed by default

v1.11.2
- Fix opengl_gt input file symlink missing

v1.11.3
- Increase max camera / object animation random walk trials
- Fix scenetype gin recognition causing crashes for underwater.gin / kelpforest.gin

v1.11.4
- Fix circular / segfaulting imports when modules imported individually
- Fix ordering-dependence in unit tests 
- Fix scenetype.gin crashes for underwater/kelpforest
- Increase integration test timelimit
- Add `analyze_crash_reasons` crash summary script
- Improve success rate of camera / creature animations via increased retry attempts

v1.12.0
- Publish to PyPi

v1.12.1
- Fix blender_gt crash from errored object in global_flat_shading
- Replace diameter with radius in butil.spawn_capsule
- Fix ignored blender_gt sample count config
- Fix outdated bbox input for camera_pose_proposal
- Bugfix stdout passthrough mode crashing due to no logfile created
- Add normalmaps to integration test viewer, misc test fixes
- Avoid rare duplicate names in indoor solver

v1.12.2
- Fix excessive time/memory/crashes in nature scenes due to inactive viewpoint filter
- Fix blendergt not set to 1hr timelimit by slurm_1h.gin
- Add get_cmd.child_debug flag
- Usability improvements for integration test scripts
- Fix static asset import #391
- Fix indoor_asset_semantics.py typo #398

v1.12.3
- Fix populate_collection missing argument 'cameras'
- Fix split_in_view crash for dist_max=None


v1.13.0
- Refactor materials into classes
- Separate test lists for new-style and deprecated apply()-style materials

v1.13.1
- Refactor transpiler, fix transpiling disabled input sockets

v1.13.2
- Bugfix invalid Brick kwargs and `1-2 args execution context is supported` during indoor room generation


v1.14.0
- Add option to densely subdivide room meshes using OcMesher
- Add RRT-Star camera pathfinding for video viewpoint animation

v1.15.0
- Initial code release for Infinigen-Sim! See ExportingToSimulators.md for guide on generating articulated doors, toasters, lamps, fridges, & dishwashers. Added articulation exporters to USD, MJCF, URDF.

v1.15.1
- Fix occlusion boundaries when polygons project to negative z in camera space

v1.15.2
- Fix house ocmesher camera crash
- Add house ocmesher example command, warnings and example images
- Update face_size_visualizer
- Standardize use of set_displacement_mode

v1.15.4
- fix empty material slot crash in blendergt
- fix empty material slot crash in export glass materials #442
- fix displacement not properly disabled when requested 443
- fix mvs cameras undefined variable #437
- fix crash in overhead run_stage #439
- disable optimize_disk_usage unless requested
- attempted to fix pypi
- fix missing studio.gin #417 by @jerrylingjiemei