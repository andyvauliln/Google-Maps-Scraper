# https://github.com/instaloader/instaloader/blob/master/instaloader/instaloader.py
# https://github.com/redianmarku/instagram-follower-scraper/blob/master/run.py
# https://github.com/iSarabjitDhiman/InstaGPy
# https://github.com/rly0nheart/instagram-location-search/
# https://github.com/t0mxplo1t/Kunai/blob/main/kunai.py

import instaloader
import sys

from instaloader import Instaloader


x = Instaloader()

try:

    f = instaloader.Profile.from_username(x.context, "baliroyalproperty")

    print("\033[32mUsername\033[0m :", f.username)
    print("\033[32mID\033[0m :", f.userid)
    print("\033[32mNama lengkap\033[0m :", f.full_name)
    print("\033[32mBiografi\033[0m :", f.biography)
    print("\033[32mNama kategori bisnis\033[0m :", f.business_category_name)
    print("\033[32mURL eksternal\033[0m :", f.external_url)
    print("\033[32mDiikuti orang\033[0m :", f.followed_by_viewer)
    print("\033[32mMengikuti\033[0m :", f.followees)
    print("\033[32mPengikut\033[0m :", f.followers)
    # print("\033[32mMengikuti orang\033[0m :", f.follows_viewer)
    # print("\033[32mDiblokir orang\033[0m :", f.blocked_by_viewer)
    # print("\033[32mPernah memblokir orang\033[0m :", f.has_blocked_viewer)
    # print("\033[32mPunya sorotan\033[0m :", f.has_highlight_reels)
    # print("\033[32mPunya cerita publik\033[0m :", f.has_public_story)
    # print("\033[32mTelah meminta orang\033[0m :", f.has_requested_viewer)
    # print("\033[32mDiminta orang\033[0m :", f.requested_by_viewer)
    # print("\033[32mMemiliki cerita yang dapat dilihat\033[0m :", f.has_viewable_story)
    # print("\033[32mIGTV\033[0m :", f.igtvcount)
    print("\033[32mAkun bisnis\033[0m :", f.is_business_account)
    print("\033[32mAkun pribadi\033[0m :", f.is_private)
    print("\033[32mDiverifikasi\033[0m :", f.is_verified)
    # print("\033[32mPostingan\033[0m :", f.mediacount)
    print("\033[32mURL foto profil\033[0m :", f.profile_pic_url)

except KeyboardInterrupt:
    print("\033[33mI understand!")

except EOFError:
    print("\033[33mWhy?")
