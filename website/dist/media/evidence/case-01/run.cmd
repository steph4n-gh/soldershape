M 2
u
g 3
r
g 30
r
g 30
hessian_seek
hessian_seek
energy_before := total_energy
g 30
hessian_seek
hessian_seek
stationarity_delta := abs(total_energy-energy_before)
do_xforce
do_zforce
eigenprobe 0
printf "SS_LEVEL 0 %d %.17g %.17g %.17g %.17g %.17g %d %.17g\n",facet_count,xforce,zforce,total_energy,body[1].volume,(body[1].volume-body[1].target)/body[1].target,eigen_neg,stationarity_delta
r
g 30
hessian_seek
hessian_seek
hessian_seek
energy_before := total_energy
g 30
hessian_seek
hessian_seek
stationarity_delta := abs(total_energy-energy_before)
do_xforce
do_zforce
eigenprobe 0
printf "SS_LEVEL 1 %d %.17g %.17g %.17g %.17g %.17g %d %.17g\n",facet_count,xforce,zforce,total_energy,body[1].volume,(body[1].volume-body[1].target)/body[1].target,eigen_neg,stationarity_delta
r
g 30
hessian_seek
hessian_seek
hessian_seek
energy_before := total_energy
g 30
hessian_seek
hessian_seek
stationarity_delta := abs(total_energy-energy_before)
do_xforce
do_zforce
eigenprobe 0
printf "SS_LEVEL 2 %d %.17g %.17g %.17g %.17g %.17g %d %.17g\n",facet_count,xforce,zforce,total_energy,body[1].volume,(body[1].volume-body[1].target)/body[1].target,eigen_neg,stationarity_delta
r
linear
recalc
{ foreach vertex vv do printf "VERTEX %d %.17g %.17g %.17g\n",vv.id,vv.x,vv.y,vv.z; foreach facet ff do printf "TRIANGLE %d %d %d %d\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id; } >>> "mesh.txt"
printf "SS_DONE %d %.17g\n",facet_count,body[1].volume
quit 0
