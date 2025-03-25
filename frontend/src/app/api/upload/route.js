import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import crypto from "crypto";

const s3 = new S3Client({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

export async function POST(req) {
  try {
    const body = await req.json();
    const fileName = body.fileName || `upload-${crypto.randomUUID()}.pdf`;

    const command = new PutObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: fileName,
      ContentType: "application/pdf",
    });

    // Generate a pre-signed URL valid for 5 minutes
    const url = await getSignedUrl(s3, command, { expiresIn: 60 * 5 });

    return Response.json({ url, fileName });
  } catch (error) {
    console.error("Error generating upload URL:", error);
    return Response.json({ error: "Failed to generate upload URL" }, { status: 500 });
  }
}
