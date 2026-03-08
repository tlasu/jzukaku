#%%
import jzukaku
# %%
zukaku = jzukaku.latlon_to_zukaku(43.068564, 141.350726)
print(zukaku.code)

bounds = [43.068564, 141.350726, 44.068564, 141.350726]
print(bounds)
bbox = jzukaku.bbox_to_zukaku(bounds, level=500)
print(bbox)
