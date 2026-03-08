#%%
import pyproj
# %%
def get_jprcs_zone(zone):
    return 6668 + zone

zone = 12
crs_4326 = pyproj.crs.CRS.from_epsg(4326)
target = get_jprcs_zone(zone)
crs_target = pyproj.crs.CRS.from_epsg(target)
transformer = pyproj.Transformer.from_crs(crs_4326, crs_target, always_xy=True)


# %%
transformer.transform(141.350726, 43.068564)
# %%
