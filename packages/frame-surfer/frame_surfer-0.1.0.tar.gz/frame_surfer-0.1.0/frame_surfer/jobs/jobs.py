import datetime
import os
from urllib.parse import quote, urlparse, urlunparse

import requests
from django.conf import settings
from nautobot.apps.jobs import BooleanVar, Job, ObjectVar, register_jobs
from nautobot.extras.choices import SecretsGroupAccessTypeChoices, SecretsGroupSecretTypeChoices
from nautobot.extras.models import SecretsGroup
from PIL import Image

from frame_surfer.api_utils import FrameSurfer
from frame_surfer.models import FrameTV, PhotoModel, UnsplashModel


class FetchRandomJob(Job):
    """
    A job that fetches a random item from a predefined list.
    """

    class Meta:
        name = "Fetch Random"
        description = "A job that fetches a random photo from unsplash based on the given parameters."

    unsplash = ObjectVar(
        model=UnsplashModel,
        description="Pick the Unsplash Service to use",
        required=True,
    )
    tv = ObjectVar(
        model=FrameTV,
        description="Pick the Frame TV to use",
        required=True,
    )
    push_to_tv = BooleanVar(
        default=True,
        description="Push the photo to the TV",
        required=False,
    )
    set_picture = BooleanVar(
        default=True,
        description="Marks the photo as the current picture on the TV",
        required=False,
    )

    def _resize_image(self, image_path):
        # Open the image
        img = Image.open(image_path)

        # Calculate the target aspect ratio dimensions for 16:9
        original_width, original_height = img.size
        target_width = original_width
        target_height = int(target_width * (9 / 16))

        # Check if the new height is larger than the original height
        if target_height > original_height:
            # Scale down width to fit the original height
            target_height = original_height
            target_width = int(target_height * (16 / 9))

        # Calculate cropping area to maintain center
        left = (original_width - target_width) // 2
        top = (original_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        # Crop the image to maintain a 16:9 aspect ratio
        cropped_img = img.crop((left, top, right, bottom))

        # Resize the image to the specified dimensions (3840x2160)
        resized_img = cropped_img.resize((3830, 2100))

        # Save the image
        resized_img.save(image_path)

    def _normalize_url(self, raw_url):
        parsed = urlparse(raw_url.strip(), scheme="https")
        if not parsed.netloc:
            parsed = parsed._replace(netloc=parsed.path, path="")
        path = quote(parsed.path)
        return urlunparse(parsed._replace(path=path))

    def _create_directory(self, path):
        self.logger.info(f"Creating directory if it does not exist: {path}")
        if not os.path.exists(path):
            self.logger.info(f"Directory does not exist, creating: {path}")
            os.makedirs(path)
        self.logger.info(f"Directory exists: {path}")

    def run(self, *, unsplash, tv, push_to_tv, set_picture, **kwargs):
        """Run the job."""
        # Get our Access Key
        secrets_group = SecretsGroup.objects.get(name=unsplash.access_key.name)
        access_key = secrets_group.get_secret_value(
            access_type=SecretsGroupAccessTypeChoices.TYPE_GENERIC, secret_type=SecretsGroupSecretTypeChoices.TYPE_TOKEN
        )
        # Fix this to be dynamic later
        url = "https://api.unsplash.com/photos/random/?w=3840&h=2160&topics=WdChqlsJN9c,6sMVjTLSkeQ&content_filter=high&orientation=landscape"
        header = {"Authorization": f"Client-ID {access_key}"}
        response = requests.get(
            url,
            headers=header,
        )
        if response.status_code != 200:
            self.logger.error(f"Failed to fetch photo: {response.status_code} - {response.text}")
            return
        data = response.json()
        # Save to Model
        normalized_url = self._normalize_url(data["urls"]["raw"])

        # we need to get the download location from the response
        img_response = requests.get(f"{data['links']['download_location']}", headers=header)
        img_response.raise_for_status()
        # We get returned URL to the image, now we can download it
        with requests.get(f"{img_response.json()['url']}", headers=header) as download_response:
            download_response.raise_for_status()
            # check to see if directory exists and create it if not
            path = f"{settings.STATIC_ROOT}/frame_surfer/{tv.name.replace( ' ', '_' ).lower()}"
            self._create_directory(path)
            with open(f"{path}/{data['id']}.jpg", "wb") as file:
                # file.write(download_response.content)
                for chunk in download_response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            # Per Unsplash API guidelines, we need to perform a GET request to track downloads
            requests.get(f"https://api.unsplash.com/photos/{data['id']}/download", stream=True, headers=header)
            self.logger.info(f"Downloaded photo {data['id']} from Unsplash")

        if push_to_tv:
            # Step 2 Resize the Photo to 16:9 aspect ratio
            self.logger.info(f"Resizing photo {data['id']} to 16:9 aspect ratio")
            resized_image = self._resize_image(f"{path}/{data['id']}.jpg")
            self.logger.info(f"{resized_image}")
            self.logger.info(type(resized_image))
            # Step 3 Push the Photo to the TV
            self.logger.info(f"Pushing photo {data['id']} to TV {tv.name}")
            frame_tv = FrameSurfer(tv.ip_address)
            uploaded_file = frame_tv.send_to_tv(f"{path}/{data['id']}.jpg")
        if set_picture:
            self.logger.info(f"Setting photo {data['id']} on TV {tv.name} at {uploaded_file}")
            frame_tv.set_picture(uploaded_file)
            # For now, we will just log that we pushed the photo
            self.logger.info(f"Pushed photo {data['id']} to TV {tv.name}")
        # save it all to the database
        photo = PhotoModel.objects.create(
            name=data["id"],
            downloaded_at=datetime.datetime.now(),
            url=normalized_url,
            tv=tv,
            tv_file_name=uploaded_file,
        )
        photo.validated_save()


class DeletePhotoJob(Job):
    tv = ObjectVar(
        model=FrameTV,
        description="Pick the Frame TV to use",
        required=True,
    )
    photo = ObjectVar(
        model=PhotoModel,
        description="Pick the Unsplash Service to use",
        required=True,
    )

    class __meta__:
        name = "Delete Photo"
        description = "A job that deletes a photo from the database and the TV."

    def run(self, *args, **kwargs):
        """Run the job."""
        photo = kwargs.get("photo")
        self.logger.info("This job is not yet implemented.")
        return


jobs = [FetchRandomJob]
register_jobs(*jobs)
